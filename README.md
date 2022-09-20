
![Banner](img/SIOL_Banner.jpg)

*Hauke Roggenkamp \| 2022-09-20*

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
`../../data/simulations/all_apps_wide.csv`[^2]) to create and analyze
the audio files we are interested in.

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
|                         1 | 1q7hm3kn         |                            8 |                                  1 | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO |                                    |
|                         2 | a6mxzk7c         |                            8 |                                  0 | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                                                                              | I donate seven points.             |
|                         3 | 9jpn239t         |                            8 |                                  1 | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO |                                    |
|                         4 | s6dp904x         |                            8 |                                  0 | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                                                                              | I donate eight points.             |
|                         5 | 367iodlj         |                            8 |                                  1 | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO |                                    |
|                         6 | bk9phvvq         |                            8 |                                  0 | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                                                                              | I donate seven points.             |

Because the data table is wide (there are 46 columns and 150 rows),
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

This leaves us with a data.table that has only 8 columns (and 150 rows)
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

# display vector
kable(long[!is.na(voiceBase64),
           .(spokenDecision)])
```

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

# display vector
kable(long[!is.na(baselineBase64),
           .(spokenBaseline)])
```

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

| session.code | participant.code | participant.label | round | voiceInterface | writtenDecision        | voiceBase64                                                                   | baselineBase64                                                                | spokenDecision         | spokenBaseline                              | spokenDecision2num | writtenDecision2num | donation | recordings | longitude                                | latitude                                 | ipAddress    | screenWidth | screenHeight | devicePixelRatio | userAgent |  Q1 |
|:-------------|:-----------------|:------------------|:------|---------------:|:-----------------------|:------------------------------------------------------------------------------|:------------------------------------------------------------------------------|:-----------------------|:--------------------------------------------|-------------------:|--------------------:|---------:|-----------:|:-----------------------------------------|:-----------------------------------------|:-------------|------------:|-------------:|-----------------:|:----------|----:|
| ey9362jm     | 05yf5o1b         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 080zoj2f         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate five points.  | I have read and understand the instructions |                  5 |                  NA |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | 0mc5rsth         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | 0t13qd90         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 0tu7oi3e         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate eight points. | I have read and understand the instructions |                  8 |                  NA |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | 0zdw127e         | NA                | 1     |              0 | I donate ten points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                  10 |       10 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | 19hdz5ea         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate one points.   | I have read and understand the instructions |                  1 |                  NA |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | 1msk5und         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate four points.  | I have read and understand the instructions |                  4 |                  NA |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | 1q7hm3kn         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate three points. | I have read and understand the instructions |                  3 |                  NA |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | 2m3ynpk2         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate one points.   | I have read and understand the instructions |                  1 |                  NA |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | 2mtx53qz         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 2yluefq4         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate one points.   | I have read and understand the instructions |                  1 |                  NA |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | 3212crb7         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 35ny32jz         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | 367iodlj         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | 37c98tiv         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate five points.  | I have read and understand the instructions |                  5 |                  NA |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | 38glghrx         | NA                | 1     |              0 | I donate three points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   3 |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 3cahttao         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | 3ohs0j1x         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 3st50o9v         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | 49pcvnl3         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate four points.  | I have read and understand the instructions |                  4 |                  NA |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | 4bsyifhs         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 4ews2v7q         | NA                | 1     |              0 | I donate five points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   5 |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 4s41z7vs         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | 4t0g1yvr         | NA                | 1     |              0 | I donate six points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   6 |        6 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | 4x2059t1         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate one points.   | I have read and understand the instructions |                  1 |                  NA |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 51a5q4qj         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate three points. | I have read and understand the instructions |                  3 |                  NA |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 5pyq25xz         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate nine points.  | I have read and understand the instructions |                  9 |                  NA |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | 5vl67fi6         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | 6heftx9o         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 6ku1vq85         | NA                | 1     |              0 | I donate six points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   6 |        6 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | 6y8spob0         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | 796kz16v         | NA                | 1     |              0 | I donate nine points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   9 |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | 7l5esqxo         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate three points. | I have read and understand the instructions |                  3 |                  NA |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | 7usbv225         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | 85mtv7l1         | NA                | 1     |              0 | I donate four points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   4 |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | 8q8lrnse         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate three points. | I have read and understand the instructions |                  3 |                  NA |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | 8xrplb0e         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate two points.   | I have read and understand the instructions |                  2 |                  NA |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | 97cerve5         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate ten points.   | I have read and understand the instructions |                 10 |                  NA |       10 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | 9jpn239t         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate four points.  | I have read and understand the instructions |                  4 |                  NA |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | 9q4gzpj8         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate four points.  | I have read and understand the instructions |                  4 |                  NA |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | a6mxzk7c         | NA                | 1     |              0 | I donate seven points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   7 |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | a93qvojh         | NA                | 1     |              0 | I donate five points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   5 |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | aezzengi         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | amsxysw3         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate five points.  | I have read and understand the instructions |                  5 |                  NA |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | biz1r9we         | NA                | 1     |              0 | I donate three points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   3 |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | bk9phvvq         | NA                | 1     |              0 | I donate seven points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   7 |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | bqrkoron         | NA                | 1     |              0 | I donate three points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   3 |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | bwvsn1ni         | NA                | 1     |              0 | I donate zero points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   0 |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | ckgswu3x         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate one points.   | I have read and understand the instructions |                  1 |                  NA |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | cwn7cntj         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | d4431tko         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | dgj0qnfl         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate four points.  | I have read and understand the instructions |                  4 |                  NA |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | dntdtup9         | NA                | 1     |              0 | I donate nine points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   9 |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | dvtmq8i0         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | e3cn7vxx         | NA                | 1     |              0 | I donate nine points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   9 |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | e8mmlo83         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate four points.  | I have read and understand the instructions |                  4 |                  NA |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | earuvdbc         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate two points.   | I have read and understand the instructions |                  2 |                  NA |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | fierp3sx         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate three points. | I have read and understand the instructions |                  3 |                  NA |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | fslau30n         | NA                | 1     |              0 | I donate five points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   5 |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | g0h9dnhv         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate zero points.  | I have read and understand the instructions |                  0 |                  NA |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | g4wodsx3         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | gszngxj8         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate one points.   | I have read and understand the instructions |                  1 |                  NA |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | h4pd2oo7         | NA                | 1     |              0 | I donate six points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   6 |        6 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | h5je7v03         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate zero points.  | I have read and understand the instructions |                  0 |                  NA |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | h5knhof5         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate three points. | I have read and understand the instructions |                  3 |                  NA |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | hnt6taeq         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | ho7i9xrs         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate two points.   | I have read and understand the instructions |                  2 |                  NA |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | hvutie0p         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate two points.   | I have read and understand the instructions |                  2 |                  NA |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | hwe42czw         | NA                | 1     |              0 | I donate seven points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   7 |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | i29e9x5g         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | i83b1enn         | NA                | 1     |              0 | I donate three points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   3 |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | ilabphgi         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | iqn5aso6         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate ten points.   | I have read and understand the instructions |                 10 |                  NA |       10 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | iv13er8o         | NA                | 1     |              0 | I donate seven points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   7 |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | j1qxkfnc         | NA                | 1     |              0 | I donate nine points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   9 |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | j1wh0yw6         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | j3zw2oew         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate zero points.  | I have read and understand the instructions |                  0 |                  NA |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | jclycd33         | NA                | 1     |              0 | I donate seven points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   7 |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | jeqj7wfh         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate nine points.  | I have read and understand the instructions |                  9 |                  NA |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | jg28t24t         | NA                | 1     |              0 | I donate three points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   3 |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | jji8op2b         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate zero points.  | I have read and understand the instructions |                  0 |                  NA |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | joeg337f         | NA                | 1     |              0 | I donate ten points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                  10 |       10 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | k5tzz57o         | NA                | 1     |              0 | I donate zero points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   0 |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | kd1o7nni         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate eight points. | I have read and understand the instructions |                  8 |                  NA |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | ki3bpt14         | NA                | 1     |              0 | I donate zero points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   0 |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | kl4h3jgo         | NA                | 1     |              0 | I donate zero points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   0 |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | km53jsxa         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | knj23r09         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate zero points.  | I have read and understand the instructions |                  0 |                  NA |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | korauhwj         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | kywe3bqz         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate nine points.  | I have read and understand the instructions |                  9 |                  NA |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | lbsd6qtj         | NA                | 1     |              0 | I donate nine points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   9 |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | ltzy9yzs         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | lvb5yxe6         | NA                | 1     |              0 | I donate ten points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                  10 |       10 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | mp0e3nt2         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate four points.  | I have read and understand the instructions |                  4 |                  NA |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | mrkjbhj0         | NA                | 1     |              0 | I donate nine points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   9 |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | mukpg2b0         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate six points.   | I have read and understand the instructions |                  6 |                  NA |        6 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | n5bj0xnd         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate ten points.   | I have read and understand the instructions |                 10 |                  NA |       10 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | n76vi3ce         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | na7tepzo         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | nap3idga         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate eight points. | I have read and understand the instructions |                  8 |                  NA |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | ndgvjjk7         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate two points.   | I have read and understand the instructions |                  2 |                  NA |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | nfscsmjq         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate ten points.   | I have read and understand the instructions |                 10 |                  NA |       10 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | nkasrpaa         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate six points.   | I have read and understand the instructions |                  6 |                  NA |        6 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | nl7pfroj         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | ntpj5z2h         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | nz4qppwb         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | o0cjeqw4         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | oft0l58g         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate eight points. | I have read and understand the instructions |                  8 |                  NA |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | ogq24ufv         | NA                | 1     |              0 | I donate zero points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   0 |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | oxchjjrj         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate eight points. | I have read and understand the instructions |                  8 |                  NA |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | qchp0nt3         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | qkc20b7u         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate nine points.  | I have read and understand the instructions |                  9 |                  NA |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | qt4nwmbc         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | qvdc759j         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate ten points.   | I have read and understand the instructions |                 10 |                  NA |       10 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | r3zryjig         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | s0yw83rv         | NA                | 1     |              0 | I donate seven points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   7 |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | s2i1qzio         | NA                | 1     |              0 | I donate two points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   2 |        2 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | s2q7uhyq         | NA                | 1     |              0 | I donate five points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   5 |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | s48f0irg         | NA                | 1     |              0 | I donate six points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   6 |        6 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | s6dp904x         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | s6s4hh7j         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate three points. | I have read and understand the instructions |                  3 |                  NA |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | sdpt8u4c         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate one points.   | I have read and understand the instructions |                  1 |                  NA |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | sgerzmlf         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate three points. | I have read and understand the instructions |                  3 |                  NA |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | snyznnhm         | NA                | 1     |              0 | I donate zero points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   0 |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | tsfh1npu         | NA                | 1     |              0 | I donate five points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   5 |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | uc5z9ove         | NA                | 1     |              0 | I donate four points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   4 |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | udfhk9xf         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate zero points.  | I have read and understand the instructions |                  0 |                  NA |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | uhl1q3l8         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate zero points.  | I have read and understand the instructions |                  0 |                  NA |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | v6865h1g         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate eight points. | I have read and understand the instructions |                  8 |                  NA |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | vbix6iis         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate five points.  | I have read and understand the instructions |                  5 |                  NA |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | vh3t9j0p         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate zero points.  | I have read and understand the instructions |                  0 |                  NA |        0 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | w19ebh4m         | NA                | 1     |              0 | I donate nine points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   9 |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | w5s7s0dt         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | w62r0iwe         | NA                | 1     |              0 | I donate five points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   5 |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | wagqashv         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | wfvzos10         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | wumcprd8         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | xh3qy9cf         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | xitakqsp         | NA                | 1     |              0 | I donate one points.   | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   1 |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | xrzubu4o         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate four points.  | I have read and understand the instructions |                  4 |                  NA |        4 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | xts3sjwe         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate nine points.  | I have read and understand the instructions |                  9 |                  NA |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | xwyu2enf         | NA                | 1     |              0 | I donate five points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   5 |        5 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | xzpo3v28         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate seven points. | I have read and understand the instructions |                  7 |                  NA |        7 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   1 |
| ey9362jm     | yd3nlyw9         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate eight points. | I have read and understand the instructions |                  8 |                  NA |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   2 |
| ey9362jm     | yov24208         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate one points.   | I have read and understand the instructions |                  1 |                  NA |        1 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | yypson7d         | NA                | 1     |              0 | I donate nine points.  | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   9 |        9 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   3 |
| ey9362jm     | z9eelnzl         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate three points. | I have read and understand the instructions |                  3 |                  NA |        3 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |
| ey9362jm     | zmqnlokx         | NA                | 1     |              1 |                        | XC8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gO… | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… | I donate ten points.   | I have read and understand the instructions |                 10 |                  NA |       10 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   5 |
| ey9362jm     | zrudmczv         | NA                | 1     |              0 | I donate eight points. | …                                                                             | fwSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIl… |                        | I have read and understand the instructions |                 NA |                   8 |        8 |          1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |         414 |          896 |                1 | I’m a bot |   4 |

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

| voiceInterface | round |     mean |
|---------------:|:------|---------:|
|              0 | 1     | 4.573333 |
|              1 | 1     | 4.813333 |

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
