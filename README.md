
![Banner](img/SIOL_Banner.jpg)

*Hauke Roggenkamp \| 2022-11-06*

# Background

This document belongs to a
[project](https://github.com/Howquez/say-it-out-loud) in which
participants of an experiment receive an endowment and can decide
whether and how much the want to donate to some charity.

Importantly, participants encounter one of two interfaces to communicate
their decision: They either type their decision using a classic text
input or they make a voice recording that we analyze using a
speech-to-text engine. Which type of interface a participant encounters
is determined randomly.

**More information:**

-   You can find the experiment’s demo
    [here](https://ibt-hsg.herokuapp.com/demo).
-   A kaban board can be found
    [here](https://github.com/users/Howquez/projects/1/views/1).

**Read further if you want to learn how Base64 strings (stemming from
recorded voice) is decoded to audio files and then converted to text
which is then converted to numeric information.**

# Workflow

1.  Run [oTree Experiment](https://ibt-hsg.herokuapp.com/demo) and
    download the resulting .csv file.
2.  Run these lines of code. They will:
    -   [decode](#decode) a Base64 string to a .wav file and store it
    -   pass these files to a [speech-to-text](#speech-to-text) API
        (Google)
3.  [extract the quantities](#words-to-numbers) from Google’s text
    output
4.  [Analyze](analysis) the data in search for a treatment effect.

# Setup

``` r
# install this package once, it'll then install and load all remaining packages
# install.packages("pacman")

pacman::p_load(rmarkdown, knitr, magrittr, data.table, stringr, lubridate, 
               base64enc, googleLanguageR, xfun)

# unfortunately, there is one github project we need where the repository's
# name does not match the package's name.
pacman::p_load_gh("fsingletonthorn/words_to_numbers")
library(wordstonumbers)
```

After installing and loading the packages, the data is loaded and stored
as a `data.table`.[^1]

``` r
# select file path based on YAML parameters
realData <- FALSE
fPath <- "../../data/simulations"

if(params$data == "Real Data"){
        realData <- TRUE
        fPath <- "../../data/raw"
}
```

``` r
# find most recent file in directory
cFiles <- file.info(list.files(path = fPath,
                               full.names = TRUE,
                               pattern = ".csv$"),
                    extra_cols = FALSE)
recentCSV <- cFiles[cFiles$mtime == max(cFiles$mtime), ] %>% row.names()
rm("cFiles")
```

Some of the columns contain `base64`-encoded strings that can be decoded
to audio files using the `base64enc` package. This implies that we only
need these lines of code as well as a single .csv file (in this case
`../../data/raw/all_apps_wide-2022-11-06.csv`[^2]) to create and analyze
the audio files we are interested in.

``` r
# read data
dt <- data.table(read.csv(file = recentCSV))
```

``` r
# rename columns
names(dt) %>% 
        str_replace_all(pattern = "dictatorGame", replacement = "dg") %>%
        str_replace_all(pattern = "\\.(player|subsession|group)", replacement = "") %>%
        str_replace_all(pattern = "\\._?", replacement = "_") %>%
        setnames(x = dt, old = names(dt))
```

``` r
# select paradata
para <- dt[,
           .(participant_id_in_session, participant_code, participant_label,
             session_code, session_label, session_is_demo, session_config_participation_fee,
             participant_index_in_pages, participant_time_started_utc,
             participant_payoff, participant_interface, participant_allowReplay,
             dg_1_longitude, dg_1_latitude, dg_1_ipAddress, dg_1_width, dg_1_height,
             dg_1_devicePixelRatio, dg_1_userAgent, dg_1_privacy_time
             )]
```

``` r
# select benchmark audio data (base64 encoded)
benchmark <- dt[,
                .(session_code, participant_code,
                  dg_1_recordings, dg_1_checkBase64, 
                  dg_2_checkBase64, dg_2_recordings,
                  dg_3_checkBase64, dg_3_recordings)]
```

``` r
# select data from allocation decision
decision <- dt[,
               .(session_code, participant_code,
                 dg_3_interface, dg_3_allowReplay, dg_3_recordings, dg_3_allocation, 
                 dg_3_writtenDecision, dg_3_spokenDecision, dg_3_decisionBase64)]
```

``` r
# select self reported data from the "outro" app
cols <- c("session_code", "participant_code", 
          str_subset(string = names(dt), pattern = "outro.*"))

selfreports <- dt[, ..cols]

rm(cols)
```

``` r
# the pattern needed is "(?<=RECORDING_2: ).*" where 2 should be a variable (dg_3_recordings)

decision[dg_3_interface == "Voice",
         dg_3_latestVoiceRecording := dg_3_spokenDecision %>% str_extract(pattern = paste0("(?<=RECORDING_", dg_3_recordings, ": ).*"))]
```

# Decode

The following lines document a for loop that decodes the relevant rows
of `voiceBase64` and stores the result in `../../data/wav/` (if you are
working with real data as declared in this document’s YAML header – if
not, the following code chunk will be skipped).

``` r
# create file names for the wav files that will be generated using a for loop
decision[dg_3_interface == "Voice",
         filePath := paste0("../../data/wav/",
                            participant_code,
                            "_decision.wav")]


# create a vector of "speaking" decisions to loop over
spokenDecisions <- decision[dg_3_interface == "Voice", filePath]

# run loop to decode and store corresponding files
for(file in spokenDecisions){
        decision[filePath == file,
           base64decode(what = dg_3_latestVoiceRecording,
                        output = file(filePath,
                                      "wb"))]
}
```

# Speech to Text

To use the voice data, I am using the `googleLanguageR` package and its
`gl_speech()` function. This requires you to
[authenticate](#authentication). Subsequently, the text is
[transcribed](#transcription) which allows us to [detect](#detection)
the amount of money participants want to donate.

## Authentication

To use that function, you need to authenticate. Click
[here](https://bookdown.org/paul/apis_for_social_scientists/google-speech-to-text-api.html#prerequisites-8)
to find out how.

I stored my key in a JSON file and read it via `gl_auth()`. You have to
enter the path to your personal key to run the next few lines.

``` r
gl_auth("../../../ibtanalytics-0ba5cc05ef54.json")
```

## Trasincription

### Real Data

The following code should only be executed if you have real data as it
is costly as Google bills 15s. per transcription[^3] If you are working
with simulated data, jump to the [simulations](#simulations) section.

#### Decision Data

Having authenticated, I create an empty character vector
`spokenDecision` that will be populated using a for loop that calls
`gl_speech()`.

``` r
# run this code chunk if working with real data. It may be too costly for
# simulated data

# populate writtenDecision vector in for loop
for(file in spokenDecisions){ # note that there is a difference between spokenDecisions & spokenDecision
        tmp <- gl_speech(audio_source = file, 
                         languageCode = "en", 
                         encoding = "FLAC",
                         sampleRateHertz = 44100,
                         customConfig = list('audio_channel_count' = 1)
                         )
        
        transcript <- tmp$transcript[,1]
        
        decision[filePath == file,
           dg_3_writtenDecision := transcript]
}
```

    ## 2022-11-06 16:39:29 -- Speech transcription finished. Total billed time: 15s

    ## 2022-11-06 16:39:30 -- Speech transcription finished. Total billed time: 15s

``` r
decision[dg_3_interface == "Voice",
         dg_3_writtenDecision] %>% kable()
```

| x                |
|:-----------------|
| I allocate $0.50 |
| I allocate $0.70 |

The quality of the transcription is rather bad, but good enough as each
of the numbers contained is correct. To listen to the corresponding
audio files, you have to browse to `../../data/wav/`. The original text
of the first three entries were *I transfer \[1, 3, 6\] point(s)*. The
last two entries should read *I donate \[7, 9\] points*.

# Words to Numbers

To extract the quantities described in `dg_3_writtenDecision` vector,
one can use the `wordstonumbers` package and apply the corresponding
function (`words_to_numbers`) to it. As this just replaces the spelled
number with a digit, one also has to remove all the characters from the
respective strings. I do so, and write the result as a numeric into a
variable called `spokenDecision2num`.

``` r
speech2number <- apply(X = decision[, .(dg_3_writtenDecision)],
                       MARGIN = 1,
                       FUN = words_to_numbers) %>%
        str_replace_all(pattern = "\\D",
                        replacement = "") %>%
        as.numeric()

decision[, spokenDecision2num := speech2number]
```

[^1]: According to the authors, `data.table` provides an enhanced
    version of `data.frame`s that reduce programming and compute time
    tremendously.

[^2]: This is the most recent data we have.

[^3]: But note that you have a free monthly contingent of 60 minutes.
