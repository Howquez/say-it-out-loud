Pre-processing
================
Hauke Roggenkamp \|
2022-08-11

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

# Setup

``` r
# install this package once, it'll then install and load all remaining packages
# install.packages("pacman")

pacman::p_load(rmarkdown, knitr, magrittr, data.table, stringr, lubridate, 
               base64enc, googleLanguageR)

# unfortunately, there is one github project we need where the repository's
# name does not match the package's name.
pacman::p_load_gh("fsingletonthorn/words_to_numbers")
library(wordstonumbers)
```

After installing and loading the packages, the data is loaded and stored
as a `data.table`.[^1]

``` r
# find most recent file in directory
cFiles <- file.info(list.files(path = "../../data/raw",
                               full.names = TRUE,
                               pattern = ".csv$"),
                    extra_cols = FALSE)
recentCSV <- cFiles[cFiles$mtime == max(cFiles$mtime), ] %>% row.names()
rm("cFiles")
```

Some of the columns contain `base64`-encoded strings that can be decoded
to audio files using the `base64enc` package. This implies that we only
need these lines of code as well as a single .csv file (in this case
`../../data/raw/all_apps_wide-2022-08-10.csv`[^2]) to create and analyze
the audio files we are interested in.

``` r
# read data
dt <- data.table(read.csv(file = recentCSV))
```

The data looks approximately[^3] as follows: There are some unique IDs
for each participant, a page index, two long strings containing the
base64 encoded information and a numeric `share` variable describing
contributions made to the charity, as well as many more columns that are
not displayed in what follows.

Importantly, there is also a treatment variable called
`D_Charity.1.player.voice_interface`. This variable determines whether
`D_Charity.1.player.share` or `D_Charity.1.player.voiceBase64` is
populated since it describes whether participants face a voice interface
or a classic numeric text input.

``` r
# display relevant columns
dt[, .(participant.id_in_session, participant.code, participant._index_in_pages,
       D_Charity.1.player.voice_interface,
       D_Charity.1.player.comprehensionAudio = D_Charity.1.player.comprehensionAudio %>% str_sub(1500, 1575) %>% paste0("..."),
       D_Charity.1.player.voiceBase64 = D_Charity.1.player.voiceBase64 %>% str_sub(1500, 1575),
       D_Charity.1.player.share)] %>%
        kable()
```

| participant.id_in_session | participant.code | participant.\_index_in_pages | D_Charity.1.player.voice_interface | D_Charity.1.player.comprehensionAudio                                         | D_Charity.1.player.voiceBase64                                               | D_Charity.1.player.share |
|--------------------------:|:-----------------|-----------------------------:|-----------------------------------:|:------------------------------------------------------------------------------|:-----------------------------------------------------------------------------|-------------------------:|
|                         1 | 25d4f778         |                            9 |                                  1 | wSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIli… | C8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gOJ |                        0 |
|                         2 | jhzaa0q9         |                            9 |                                  0 | NKvZ/y8cdDTHIZQLR/7hnMesxwP/FOtG9EwIkoyYGJh1yYgaBvRA2AF/0l5LTcUJ3iLTp0Px2yRW… |                                                                              |                        2 |
|                         3 | g4n94ash         |                            9 |                                  1 | C9I05jJb4LtPXG7YkW1IvxWCO0IzjzKAo3ty+1E92B83UIpCZQWP5OwWEa0uctO7X4OSVudf5WUG… | zx6Z6JQGf4XQjqqayc72TOvXhlJZdzfwKhOLCnWwaup2XkaKxf395aJyvtKlyPacgVBKlnWCbYLl |                        0 |
|                         4 | iwf4pomn         |                            9 |                                  0 | 6DAqC0PjEh3xzcq/PR2nwRvHfspcadg2kJJtThHiM4qufLKbKKYzGqeidrheyztBABAroHfRYlvZ… |                                                                              |                        4 |
|                         5 | 7i44ihk8         |                            9 |                                  1 | 4o0LGfoCDagqHUA9vQeCAc3k2dvDcgOTLp0Wcbrm+Prgqvm9XV209FXLESKzaXLEJzxZRKWRvbjC… | HSLRYXL8UOwwciAUtQJW9XfjorG4iYAkG6E/CKCnPiAVwjQC+UtRSN8SzrDjPqQfpI97EhbgvSbl |                        0 |
|                         6 | m3vsiux8         |                            9 |                                  0 | /UCovJr14YxAWkzAm3v/jRfzYBE6KgiZkbjOGRGrzFX7S8I/93rJEpPlAyBGVFJIxDTwoyYRul2T… |                                                                              |                        6 |
|                         7 | m90jm1ji         |                            9 |                                  1 | MmTjcsgqHXlRoeI/Cs9VbtQd6kbcwX8TT5t0lC4xFeQL9FuiU3IAKdoWl6u1r6W6hW/JYqxq+MAh… | LzuabS3bfYqqGBwS3f0xmblvNoBVD3bszX9DgJOqYZt5yUs2q/OvAWyO1NKRyWFJs20FGkK16SKF |                        0 |
|                         8 | rmxckjs7         |                            9 |                                  0 | LXeLU/Cq0w5UEX5s55ePYjHTbAwdeL55Y95Al1qG8Z7tfJnI1qd+AjHMKh1JGozqhUQGy27Y5Xsv… |                                                                              |                        8 |
|                         9 | ca7dafrv         |                            9 |                                  1 | ZkvSvcVnf760p+qYLgV45H5J2k8ab8MVUr/eqgth8DK9LhVWz+swNbLRXW7iYGTSHeTBHG7ZNx8S… | EF5akp9Vc9RaIV0LX4w4Gxm4yGXOYTHcrZSX6lCglkrGAYQLVfbyNNPbnhUq0+bBZC1L8l1BxhkS |                        0 |
|                        10 | h22unu4v         |                            9 |                                  0 | /HZB0r6cq58jtLu4MaCu4oyf0bq94J/uPUu14dYVMMQqCz4fwuGMuB4w3iK2OzbdfIxZcdmRLy6x… |                                                                              |                       10 |

Because the data table is wide (there are 107 columns and 10 rows),
variables, that are measured multiple times, are arranged in separate
columns. I rearrange it using `melt()`. I then select columns that
change over time.

``` r
# melt, i.e. create long data table
tmp <- melt(data = dt,
            measure = patterns("share$", "voiceBase64$", "comprehensionAudio$"),
            value.name = c("share", "voiceBase64", "baselineBase64"),
            variable.name = "round")

# select ID columns as well as columns that represent variables of interest
long <- tmp[,
            .(session.code,
              participant.code,
              participant.label,
              round,
              voiceInterface = D_Charity.1.player.voice_interface,
              share,
              voiceBase64,
              baselineBase64)]
```

This leaves us with da data.table that has only 8 columns (and 50 rows)
which is more handy to analyze.

Note that I also renamed the variables along the way.[^4]

# Decode

The following lines document a for loop that decodes the relevant rows
of `voiceBase64` and stores the result in `../../data/wav/`.

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

### Decision Data

Having done so, I create an empty character vector `spokenDecision` that
will be populated using a for loop that calls `gl_speech()`.

``` r
# initiate empty vector
long[, spokenDecision := as.character("")]

# populate vector in for loop
for(file in spokenDecisions){ # note that there is a difference between spokenDecisions & spokenDecision
        tmp <- gl_speech(audio_source = file, 
                         languageCode = "en", 
                         encoding = "FLAC", 
                         sampleRateHertz = 44100, 
                         customConfig = list('audio_channel_count' = 1))
        
        transcript <- tmp$transcript[,1]
        
        long[decisionFilePath == file,
           spokenDecision := transcript]
}
```

    ## 2022-08-11 11:56:25 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:26 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:27 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:28 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:29 -- Speech transcription finished. Total billed time: 15s

``` r
# display vector
kable(long[!is.na(voiceBase64),
           .(spokenDecision)])
```

| spokenDecision             |
|:---------------------------|
| I transfer one point       |
|                            |
| I transferred three points |
|                            |
| I transferred six points   |
|                            |
| eidolon seven points       |
|                            |
| I don’t even nine euros    |
|                            |

The quality of the transcription is rather bad, but good enough as each
of the numbers contained is correct. To listen to the corresponding
audio files, you have to browse to `../../data/wav/`. The original text
of the first three entries were *I transfer \[1, 3, 6\] point(s)*. The
last two entries should read *I donate \[7, 9\] points*.

### Baseline Data

Because I also have the baseline recordings where participants say *I
have read and understand the instructions*, we can transcribe them as
well. Since I do not intend to analyze the content, I set the
corresponding code chunk option such that the following few lines are
not evaluated. This implies, that I will not use the information in what
follows until some voice analytics is applied.

``` r
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

    ## 2022-08-11 11:56:30 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:31 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:32 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:33 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:34 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:35 -- Speech transcription finished. Total billed time: 0s

    ## 2022-08-11 11:56:36 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:37 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:38 -- Speech transcription finished. Total billed time: 15s

    ## 2022-08-11 11:56:39 -- Speech transcription finished. Total billed time: 15s

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
| NA                                          |
| I have read and understand the instructions |
| I have read and understand the instructions |
| I threatened understand the instructions    |
| I Fresno understand the instructor          |

# Words to Numbers

To extract the quantities described in the `spokenDecision` vector, one
can use the `wordstonumbers` package and apply the corresponding
function (`words_to_numbers`) to it. As this just replaces the spelled
number with a digit, one also has to remove all the characters from the
respective strings. I do so, and write the result as a numeric into a
variable called `spokenDecision2text`.

**Note** that for each of these transcriptions, Google bills 15s.[^5]

``` r
speechtotext <- apply(X = long[,.(spokenDecision)],
                      MARGIN = 1,
                      FUN = words_to_numbers) %>%
        str_replace_all(pattern = "\\D",
                        replacement = "") %>%
        as.numeric()

long[, spokenDecision2text := speechtotext]
```

Ultimately, this variable can be blended with `share`, such that we have
one column that contains the donations of all participants. This
variable, I call this variable `donation`, is our primary outcome. We
expect it to differ between the two treatments.[^6]

``` r
# create donation variable
long[, donation := share]
long[!is.na(spokenDecision2text), donation := spokenDecision2text]
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

| session.code | participant.code | participant.label | round | voiceInterface | share | voiceBase64                                                                   | baselineBase64                                                                | decisionFilePath                      | baselineFilePath                     | spokenDecision             | spokenBaseline                              | spokenDecision2text | donation | longitude                                | latitude                                 | ipAddress    | screenWidth | screenHeight | devicePixelRatio | userAgent                                                                                                             | Q1  |
|:-------------|:-----------------|:------------------|:------|---------------:|------:|:------------------------------------------------------------------------------|:------------------------------------------------------------------------------|:--------------------------------------|:-------------------------------------|:---------------------------|:--------------------------------------------|--------------------:|---------:|:-----------------------------------------|:-----------------------------------------|:-------------|------------:|-------------:|-----------------:|:----------------------------------------------------------------------------------------------------------------------|:----|
| h6f8wa3g     | 25d4f778         | NA                | 1     |              1 |     0 | C8Qscnf7Ti3FJOu1LSf5gb0QqfiQvC3yl0U3phsToSwYdSPs7ytMrPhUHUz68zZ11/DdeTd68gOJ… | wSpl0+xKjG1jCZvjrnroFn9exSObk/AGNv2QrauUaz9BPi+1btpn4cPlFdiUaf1SWRcdGEP2mIli… | ../../data/wav/25d4f778_desicion1.wav | ../../data/wav/25d4f778_baseline.wav | I transfer one point       | I have read and understand the instructions |                   1 |        1 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | 25d4f778         | NA                | 2     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/25d4f778_desicion2.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | 25d4f778         | NA                | 3     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/25d4f778_desicion3.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | 25d4f778         | NA                | 4     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/25d4f778_desicion4.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | 25d4f778         | NA                | 5     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/25d4f778_desicion5.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | 7i44ihk8         | NA                | 1     |              1 |     0 | HSLRYXL8UOwwciAUtQJW9XfjorG4iYAkG6E/CKCnPiAVwjQC+UtRSN8SzrDjPqQfpI97EhbgvSbl… | 4o0LGfoCDagqHUA9vQeCAc3k2dvDcgOTLp0Wcbrm+Prgqvm9XV209FXLESKzaXLEJzxZRKWRvbjC… | ../../data/wav/7i44ihk8_desicion1.wav | ../../data/wav/7i44ihk8_baseline.wav | I transferred six points   | I have read and understand the instructions |                   6 |        6 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | 7i44ihk8         | NA                | 2     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/7i44ihk8_desicion2.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | 7i44ihk8         | NA                | 3     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/7i44ihk8_desicion3.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | 7i44ihk8         | NA                | 4     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/7i44ihk8_desicion4.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | 7i44ihk8         | NA                | 5     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/7i44ihk8_desicion5.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | ca7dafrv         | NA                | 1     |              1 |     0 | EF5akp9Vc9RaIV0LX4w4Gxm4yGXOYTHcrZSX6lCglkrGAYQLVfbyNNPbnhUq0+bBZC1L8l1BxhkS… | ZkvSvcVnf760p+qYLgV45H5J2k8ab8MVUr/eqgth8DK9LhVWz+swNbLRXW7iYGTSHeTBHG7ZNx8S… | ../../data/wav/ca7dafrv_desicion1.wav | ../../data/wav/ca7dafrv_baseline.wav | I don’t even nine euros    | I threatened understand the instructions    |                   9 |        9 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | ca7dafrv         | NA                | 2     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/ca7dafrv_desicion2.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | ca7dafrv         | NA                | 3     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/ca7dafrv_desicion3.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | ca7dafrv         | NA                | 4     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/ca7dafrv_desicion4.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | ca7dafrv         | NA                | 5     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/ca7dafrv_desicion5.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | g4n94ash         | NA                | 1     |              1 |     0 | zx6Z6JQGf4XQjqqayc72TOvXhlJZdzfwKhOLCnWwaup2XkaKxf395aJyvtKlyPacgVBKlnWCbYLl… | C9I05jJb4LtPXG7YkW1IvxWCO0IzjzKAo3ty+1E92B83UIpCZQWP5OwWEa0uctO7X4OSVudf5WUG… | ../../data/wav/g4n94ash_desicion1.wav | ../../data/wav/g4n94ash_baseline.wav | I transferred three points | I have read and understand the instructions |                   3 |        3 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | g4n94ash         | NA                | 2     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/g4n94ash_desicion2.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | g4n94ash         | NA                | 3     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/g4n94ash_desicion3.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | g4n94ash         | NA                | 4     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/g4n94ash_desicion4.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | g4n94ash         | NA                | 5     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/g4n94ash_desicion5.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | h22unu4v         | NA                | 1     |              0 |    10 | …                                                                             | /HZB0r6cq58jtLu4MaCu4oyf0bq94J/uPUu14dYVMMQqCz4fwuGMuB4w3iK2OzbdfIxZcdmRLy6x… | NA                                    | ../../data/wav/h22unu4v_baseline.wav |                            | I Fresno understand the instructor          |                  NA |       10 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | h22unu4v         | NA                | 2     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | h22unu4v         | NA                | 3     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | h22unu4v         | NA                | 4     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | h22unu4v         | NA                | 5     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | iwf4pomn         | NA                | 1     |              0 |     4 | …                                                                             | 6DAqC0PjEh3xzcq/PR2nwRvHfspcadg2kJJtThHiM4qufLKbKKYzGqeidrheyztBABAroHfRYlvZ… | NA                                    | ../../data/wav/iwf4pomn_baseline.wav |                            | I have read and understand the instructions |                  NA |        4 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | iwf4pomn         | NA                | 2     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | iwf4pomn         | NA                | 3     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | iwf4pomn         | NA                | 4     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | iwf4pomn         | NA                | 5     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | jhzaa0q9         | NA                | 1     |              0 |     2 | …                                                                             | NKvZ/y8cdDTHIZQLR/7hnMesxwP/FOtG9EwIkoyYGJh1yYgaBvRA2AF/0l5LTcUJ3iLTp0Px2yRW… | NA                                    | ../../data/wav/jhzaa0q9_baseline.wav |                            | I have read and understand the instructions |                  NA |        2 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | jhzaa0q9         | NA                | 2     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | jhzaa0q9         | NA                | 3     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | jhzaa0q9         | NA                | 4     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | jhzaa0q9         | NA                | 5     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m3vsiux8         | NA                | 1     |              0 |     6 | …                                                                             | /UCovJr14YxAWkzAm3v/jRfzYBE6KgiZkbjOGRGrzFX7S8I/93rJEpPlAyBGVFJIxDTwoyYRul2T… | NA                                    | ../../data/wav/m3vsiux8_baseline.wav |                            | NA                                          |                  NA |        6 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m3vsiux8         | NA                | 2     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m3vsiux8         | NA                | 3     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m3vsiux8         | NA                | 4     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m3vsiux8         | NA                | 5     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m90jm1ji         | NA                | 1     |              1 |     0 | LzuabS3bfYqqGBwS3f0xmblvNoBVD3bszX9DgJOqYZt5yUs2q/OvAWyO1NKRyWFJs20FGkK16SKF… | MmTjcsgqHXlRoeI/Cs9VbtQd6kbcwX8TT5t0lC4xFeQL9FuiU3IAKdoWl6u1r6W6hW/JYqxq+MAh… | ../../data/wav/m90jm1ji_desicion1.wav | ../../data/wav/m90jm1ji_baseline.wav | eidolon seven points       | I have read and understand the instructions |                   7 |        7 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m90jm1ji         | NA                | 2     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/m90jm1ji_desicion2.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m90jm1ji         | NA                | 3     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/m90jm1ji_desicion3.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m90jm1ji         | NA                | 4     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/m90jm1ji_desicion4.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | m90jm1ji         | NA                | 5     |              1 |     0 | NA                                                                            | NA                                                                            | ../../data/wav/m90jm1ji_desicion5.wav | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | rmxckjs7         | NA                | 1     |              0 |     8 | …                                                                             | LXeLU/Cq0w5UEX5s55ePYjHTbAwdeL55Y95Al1qG8Z7tfJnI1qd+AjHMKh1JGozqhUQGy27Y5Xsv… | NA                                    | ../../data/wav/rmxckjs7_baseline.wav |                            | I have read and understand the instructions |                  NA |        8 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | rmxckjs7         | NA                | 2     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | rmxckjs7         | NA                | 3     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | rmxckjs7         | NA                | 4     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |
| h6f8wa3g     | rmxckjs7         | NA                | 5     |              0 |     0 | NA                                                                            | NA                                                                            | NA                                    | NA                                   |                            |                                             |                  NA |        0 | User denied the request for Geolocation. | User denied the request for Geolocation. | 130.82.29.23 |        1680 |         1050 |                2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 | NA  |

[^1]: According to the authors, `data.table` provides an enhanced
    version of `data.frame`s that reduce programming and compute time
    tremendously.

[^2]: This is the most recent data we have.

[^3]: I changed the order of some selected columns and truncated the
    long strings for illustrative purposes.

[^4]: In a long format, the variables do not correspond to observations
    in a specific period, which is one of the reasons I can truncate the
    columns’ naming considerably.

[^5]: Also note that you have a free monthly contigent of 60 minutes.

[^6]: To put it differently, `spokenDecision2text` and `share` should
    differ.
