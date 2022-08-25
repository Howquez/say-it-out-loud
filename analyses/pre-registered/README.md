Data processing
================
Hauke Roggenkamp \|
2022-08-17

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

You can find the experiment’s demo
[here](https://ibt-hsg.herokuapp.com/demo).

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
`../../data/raw/all_apps_wide-2022-08-17_chrome.csv`[^2]) to create and
analyze the audio files we are interested in.

``` r
# read data
dt <- data.table(read.csv(file = recentCSV))
```

The data looks approximately[^3] as follows: There are some unique IDs
for each participant, a page index, two long strings containing the
base64 encoded information and a numeric `writtenDecision` variable
describing contributions made to the charity, as well as many more
columns that are not displayed in what follows.

Importantly, there is also a treatment variable called
`D_Charity.1.player.voice_interface`. This variable determines whether
`D_Charity.1.player.writtenDecision` or `D_Charity.1.player.voiceBase64`
is populated since it describes whether participants face a voice
interface or a classic numeric text input.

``` r
# display relevant columns
dt[, .(participant.id_in_session, participant.code, participant._index_in_pages,
       D_Charity.1.player.voice_interface,
       D_Charity.1.player.comprehensionAudio = D_Charity.1.player.comprehensionAudio %>% str_sub(1500, 1575) %>% paste0("..."),
       D_Charity.1.player.voiceBase64 = D_Charity.1.player.voiceBase64 %>% str_sub(1500, 1575),
       D_Charity.1.player.writtenDecision)] %>%
        head() %>% 
        kable()
```

| participant.id_in_session | participant.code | participant.\_index_in_pages | D_Charity.1.player.voice_interface | D_Charity.1.player.comprehensionAudio                                         | D_Charity.1.player.voiceBase64                                               | D_Charity.1.player.writtenDecision |
|--------------------------:|:-----------------|-----------------------------:|-----------------------------------:|:------------------------------------------------------------------------------|:-----------------------------------------------------------------------------|:-----------------------------------|
|                         1 | 5z2b25xt         |                            8 |                                  1 | 0O/By8AHlnwmf2a5n9BUkvUv6r6OZet41F/ujQTiBALOAe4NjZRI/Hqoijuno9Vr0uXqUFOTwMh3… | MQNxxz7uS+hDrOuJI+A+wpj8jz4WYbsTmK6aXzSbzgZhylG/ro0FFgQC0gHuDbG0SOWbSmKvYxj2 |                                    |
|                         2 | o2zofkq7         |                            8 |                                  0 | ia2sW1pKf2Bs99LXDbKps9kLeR9NE5CYb+ae2ciH9jnqJqdbxyScqClwQaAuVtXzuBlF3NpAdh+h… |                                                                              | I transfer one point.              |
|                         3 | gfx1d68g         |                            8 |                                  1 | VPe68u6NBU4EAs4B7g3FsDxiIpoL2TTL7MsYVW+GkEoGZT2sfCPgCNcPfibE+H5N9S32JAkcB+bu… | I1pBgkysaRZYGjm/C3XUtZdf0/1+JA+Q5rEqDu45Xx5CYPUfkrh0tTAvX9h0J33gu4lrjbu3qb32 |                                    |
|                         4 | rn5rrjsb         |                            8 |                                  0 | jQU6BALSAe4NsaA8YY8w9VYdKNV3LB1syc9pSPMLRHl2mBXNozPDpRbd4YxaJ6KNZ8ZeDilEcs8q… |                                                                              | I transfer three points.           |
|                         5 | 4mauisjn         |                            8 |                                  1 | HWL//0E1ZyjZ3t7zE55FI5OfufvCzc1j+p9CivvGydZBhlHU9vWePjDK4D82UmiHVL7bnv3snV+M… | 7o0EqgQCzgHuDYWMNMPn5EUJ+X0ISNcieIp0FXrriYet3+SYSpVK6QW1Gzir/0b1Q27OtTpcu5xv |                                    |

Because the data table is wide (there are 46 columns and 5 rows),
variables, that are measured multiple times, are arranged in separate
columns. I rearrange it using `melt()`. I then select columns that
change over time.

``` r
# melt, i.e. create long data table
tmp <- melt(data = dt,
            measure = patterns("writtenDecision$", "voiceBase64$", "comprehensionAudio$"),
            value.name = c("writtenDecision", "voiceBase64", "baselineBase64"),
            variable.name = "round")

# select ID columns as well as columns that represent variables of interest
long <- tmp[,
            .(session.code,
              participant.code,
              participant.label,
              round,
              voiceInterface = D_Charity.1.player.voice_interface,
              writtenDecision,
              voiceBase64,
              baselineBase64)]
```

This leaves us with a data.table that has only 8 columns (and 5 rows)
which is more handy to analyze.

Note that I also renamed the variables along the way.[^4]

# Decode

The following lines document a for loop that decodes the relevant rows
of `voiceBase64` and stores the result in `../../data/wav/` (if you are
working with real data as declared in this document’s YAML header – if
not, the following code chunk will be skipped).

``` r
# create file names for the wav files that will be generated using a for loop
long[voiceInterface == 1,
   decisionFilePath := paste0("../../data/wav/",
                       participant.code,
                       "_desicion", # to distinguish between decisions and the baseline
                       round,
                       ".wav")]

long[!is.na(baselineBase64),
   baselineFilePath := paste0("../../data/wav/",
                       participant.code,
                       "_baseline", # to distinguish between decisions and the baseline
                       ".wav")]

# create a vector of "speaking" decisions to loop over
spokenDecisions <- long[!is.na(decisionFilePath) & !is.na(voiceBase64),
                          decisionFilePath]

# run loop to decode and store corresponding files
for(file in spokenDecisions){
        long[decisionFilePath == file,
           base64decode(what = voiceBase64,
                        output = file(decisionFilePath,
                                      "wb"))]
}

# repeat the last two steps for baseline audios
baselines <- long[!is.na(baselineBase64), baselineFilePath]
rm(file)
for(file in baselines){
        long[baselineFilePath == file,
           base64decode(what = baselineBase64,
                        output = file(baselineFilePath,
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
is costly as Google bills 15s. per transcription[^5] If you are working
with simulated data, jump to the [simulations](#simulations) section.

#### Decision Data

Having authenticated, I create an empty character vector
`spokenDecision` that will be populated using a for loop that calls
`gl_speech()`.

``` r
# run this code chunk if working with real data. It may be too costly for
# simulated data

# initiate empty vector
long[, spokenDecision := as.character("")]

# populate vector in for loop
for(file in spokenDecisions){ # note that there is a difference between spokenDecisions & spokenDecision
        tmp <- gl_speech(audio_source = file, 
                         languageCode = "en", 
                         encoding = "FLAC",
                         sampleRateHertz = 44100,
                         customConfig = list('audio_channel_count' = 1)
                         )
        
        transcript <- tmp$transcript[,1]
        
        long[decisionFilePath == file,
           spokenDecision := transcript]
}
```

    ## 2022-08-17 16:21:37 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-17 16:21:38 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-17 16:21:39 -- Speech transcription finished. Total billed time: 15s

``` r
# display vector
kable(long[!is.na(voiceBase64),
           .(spokenDecision)])
```

| spokenDecision         |
|:-----------------------|
| I transfer one point   |
|                        |
| itransfer free poems   |
|                        |
| I transfer Five Points |

The quality of the transcription is rather bad, but good enough as each
of the numbers contained is correct. To listen to the corresponding
audio files, you have to browse to `../../data/wav/`. The original text
of the first three entries were *I transfer \[1, 3, 6\] point(s)*. The
last two entries should read *I donate \[7, 9\] points*.

#### Baseline Data

Because I also have the baseline recordings where participants say *I
have read and understand the instructions*, we can transcribe them as
well. Since I do not intend to analyze the content, I set the
corresponding code chunk option such that the following few lines are
not evaluated. This implies, that I will not use the information in what
follows until some voice analytics is applied.

``` r
# run this code chunk if working with real data. It may be too costly for
# simulated data

# initiate empty vector
long[, spokenBaseline := as.character("")]

# populate vector in for loop
for(file in baselines){
        tmp <- gl_speech(audio_source = file, 
                         languageCode = "en", 
                         encoding = "FLAC", 
                         sampleRateHertz = 44100, 
                         customConfig = list('audio_channel_count' = 1))
        
        transcript <- tmp$transcript[,1]
        
        long[baselineFilePath == file,
           spokenBaseline := transcript]
}
```

    ## 2022-08-17 16:21:40 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-17 16:21:41 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-17 16:21:42 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-17 16:21:43 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-17 16:21:44 -- Speech transcription finished. Total billed time: 15s

``` r
# display vector
kable(long[!is.na(baselineBase64),
           .(spokenBaseline)])
```

| spokenBaseline                              |
|:--------------------------------------------|
| I have read and understand the instructions |
| I have read and understand the instructions |
| I have read and understand the instructions |
| I have read and understand the instructions |
| I have read and understand the instructions |

### Simulations

If you do not want to spend money, execute the following code chunks.
They will not call the [Google
Speech-to-Text](https://cloud.google.com/speech-to-text/) such that you
won’t get billed. Be aware that the following chunks just pretend to
transcribe voice data, though.

``` r
# create random ints, convert them to text and paste them into a sentence
long[, spokenDecision := as.character("")]
randint <- sample(x = 0:10,
                  replace = TRUE,
                  size = long[voiceInterface == 1, .N]) %>% 
        n2w()

long[voiceInterface == 1,
     spokenDecision := paste0("I donate ", randint, " points.")]
```

``` r
# also fake the sentence where participants confirm their understanding
long[, spokenBaseline := "I have read and understand the instructions"]
```

# Words to Numbers

To extract the quantities described in the `spokenDecision` vector, one
can use the `wordstonumbers` package and apply the corresponding
function (`words_to_numbers`) to it. As this just replaces the spelled
number with a digit, one also has to remove all the characters from the
respective strings. I do so, and write the result as a numeric into a
variable called `spokenDecision2num`.

``` r
speech2number <- apply(X = long[,.(spokenDecision)],
                       MARGIN = 1,
                       FUN = words_to_numbers) %>%
        str_replace_all(pattern = "\\D",
                        replacement = "") %>%
        as.numeric()

long[, spokenDecision2num := speech2number]
```

Ultimately, this variable can be blended with `writtenDecision`, such
that we have one column that contains the donations of all participants.
To do so, I need to extract the numeric information the variable
contains. Hence, I’ll repeat the last code chunk on that variable.

``` r
text2number <- apply(X = long[,.(writtenDecision)],
                       MARGIN = 1,
                       FUN = words_to_numbers) %>%
        str_replace_all(pattern = "\\D",
                        replacement = "") %>%
        as.numeric()

long[, writtenDecision2num := text2number]
```

The blended variable, I call it `donation`, is our primary outcome. We
expect it to differ between the two treatments.[^6]

``` r
# create donation variable
long[, donation := writtenDecision2num]
long[!is.na(spokenDecision2num), donation := spokenDecision2num]
```

# Result

Finally, one can select some technical covariates (`techC`) as well as
covariates stemming from the questionnaire (`questC`) that do not change
within the session and merge them to the `long` data.table.

``` r
# create DT with technical covariates from first period
# (assuming they are constant across rounds)
techC <- dt[,
            .(session.code,
              participant.code,
              participant.label,
              recordings       = D_Charity.1.player.recordings, # need to assess that in each round
              longitude        = D_Charity.1.player.longitude,
              latitude         = D_Charity.1.player.latitude,
              ipAddress        = D_Charity.1.player.ipAddress,
              screenWidth      = D_Charity.1.player.width,
              screenHeight     = D_Charity.1.player.height,
              devicePixelRatio = D_Charity.1.player.devicePixelRatio,
              userAgent        = D_Charity.1.player.userAgent)]

# merge
long <- data.table::merge.data.table(x = long,
                                     y = techC,
                                     by = c("session.code",
                                            "participant.code",
                                            "participant.label"))
```

``` r
# create DT with covariates from questionnaire
questC <- dt[,
             .(session.code,
               participant.code,
               participant.label,
               Q1 = D_Charity.1.player.comp_1)]

# merge
long <- data.table::merge.data.table(x = long,
                                     y = questC,
                                     by = c("session.code",
                                            "participant.code",
                                            "participant.label"))
```

The resulting data looks as follows.

``` r
display <- long
display[!is.na(voiceBase64), voiceBase64 := voiceBase64 %>% str_sub(1500, 1575) %>% paste0("...")]
display[!is.na(baselineBase64), baselineBase64 := baselineBase64 %>% str_sub(1500, 1575) %>% paste0("...")]
kable(display)
```

| session.code | participant.code | participant.label | round | voiceInterface | writtenDecision          | voiceBase64                                                                   | baselineBase64                                                                | decisionFilePath                      | baselineFilePath                     | spokenDecision         | spokenBaseline                              | spokenDecision2num | writtenDecision2num | donation | recordings | longitude                                | latitude                                 | ipAddress    | screenWidth | screenHeight | devicePixelRatio | userAgent                                                                                                                                    |  Q1 |
|:-------------|:-----------------|:------------------|:------|---------------:|:-------------------------|:------------------------------------------------------------------------------|:------------------------------------------------------------------------------|:--------------------------------------|:-------------------------------------|:-----------------------|:--------------------------------------------|-------------------:|--------------------:|---------:|-----------:|:-----------------------------------------|:-----------------------------------------|:-------------|------------:|-------------:|-----------------:|:---------------------------------------------------------------------------------------------------------------------------------------------|----:|
| ubku8bsn     | 4mauisjn         | NA                | 1     |              1 |                          | 7o0EqgQCzgHuDYWMNMPn5EUJ+X0ISNcieIp0FXrriYet3+SYSpVK6QW1Gzir/0b1Q27OtTpcu5xv… | HWL//0E1ZyjZ3t7zE55FI5OfufvCzc1j+p9CivvGydZBhlHU9vWePjDK4D82UmiHVL7bnv3snV+M… | ../../data/wav/4mauisjn_desicion1.wav | ../../data/wav/4mauisjn_baseline.wav | I transfer Five Points | I have read and understand the instructions |                  5 |                  NA |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36                        |   5 |
| ubku8bsn     | 5z2b25xt         | NA                | 1     |              1 |                          | MQNxxz7uS+hDrOuJI+A+wpj8jz4WYbsTmK6aXzSbzgZhylG/ro0FFgQC0gHuDbG0SOWbSmKvYxj2… | 0O/By8AHlnwmf2a5n9BUkvUv6r6OZet41F/ujQTiBALOAe4NjZRI/Hqoijuno9Vr0uXqUFOTwMh3… | ../../data/wav/5z2b25xt_desicion1.wav | ../../data/wav/5z2b25xt_baseline.wav | I transfer one point   | I have read and understand the instructions |                  1 |                  NA |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                2 | Mozilla/5.0 (iPhone; CPU iPhone OS 13_2\_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 |   1 |
| ubku8bsn     | gfx1d68g         | NA                | 1     |              1 |                          | I1pBgkysaRZYGjm/C3XUtZdf0/1+JA+Q5rEqDu45Xx5CYPUfkrh0tTAvX9h0J33gu4lrjbu3qb32… | VPe68u6NBU4EAs4B7g3FsDxiIpoL2TTL7MsYVW+GkEoGZT2sfCPgCNcPfibE+H5N9S32JAkcB+bu… | ../../data/wav/gfx1d68g_desicion1.wav | ../../data/wav/gfx1d68g_baseline.wav | itransfer free poems   | I have read and understand the instructions |                 NA |                  NA |       NA |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36                        |   3 |
| ubku8bsn     | o2zofkq7         | NA                | 1     |              0 | I transfer one point.    | …                                                                             | ia2sW1pKf2Bs99LXDbKps9kLeR9NE5CYb+ae2ciH9jnqJqdbxyScqClwQaAuVtXzuBlF3NpAdh+h… | NA                                    | ../../data/wav/o2zofkq7_baseline.wav |                        | I have read and understand the instructions |                 NA |                   1 |        1 |         NA | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36                        |   2 |
| ubku8bsn     | rn5rrjsb         | NA                | 1     |              0 | I transfer three points. | …                                                                             | jQU6BALSAe4NsaA8YY8w9VYdKNV3LB1syc9pSPMLRHl2mBXNozPDpRbd4YxaJ6KNZ8ZeDilEcs8q… | NA                                    | ../../data/wav/rn5rrjsb_baseline.wav |                        | I have read and understand the instructions |                 NA |                   3 |        3 |         NA | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36                        |   4 |

``` r
# save data as rda and csv files
save(long, file = "../../data/processed/longData.rda")
write.csv(long, file = "../../data/processed/longData.csv")
```

# Analysis

``` r
long[round == 1,
     .(mean = mean(donation, na.rm = TRUE)),
     by = c("voiceInterface", "round")] %>% 
        kable()
```

| voiceInterface | round | mean |
|---------------:|:------|-----:|
|              1 | 1     |    3 |
|              0 | 1     |    2 |

[^1]: According to the authors, `data.table` provides an enhanced
    version of `data.frame`s that reduce programming and compute time
    tremendously.

[^2]: This is the most recent data we have.

[^3]: I changed the order of some selected columns and truncated the
    long strings for illustrative purposes.

[^4]: In a long format, the variables do not correspond to observations
    in a specific period, which is one of the reasons I can truncate the
    columns’ naming considerably.

[^5]: But note that you have a free monthly contingent of 60 minutes.

[^6]: To put it differently, `spokenDecision2num` and
    `writtenDecision2text` should differ.
