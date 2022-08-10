Pre-processing
================
Hauke Roggenkamp \|
2022-08-10

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

------------------------------------------------------------------------

# Setup

``` r
# install this package once, it'll then install and load all remaining packages
# install.packages("pacman")

pacman::p_load(rmarkdown, knitr, magrittr, data.table, stringr, lubridate, base64enc)
```

After installing and loading the packages, the data is loaded and stored
as a `data.table`.[^1] Some of the columns[^2] contain `base64` strings
that can be converted to audio files using the `base64enc` package.

``` r
# find most recent file in directory
cFiles <- file.info(list.files(path = "../../data/raw",
                               full.names = TRUE,
                               pattern = ".csv$"),
                    extra_cols = FALSE)
recentCSV <- cFiles[cFiles$mtime == max(cFiles$mtime), ] %>% row.names()
rm("cFiles")
```

This implies that we only need these lines of code as well as a single
.csv file (in this case
`../../data/raw/all_apps_wide-2022-08-10.csv`[^3]) to create and analyze
the audio files we are interested in.

``` r
# read data
dt <- data.table(read.csv(file = recentCSV))
```

The data looks approximately[^4] as follows: There are some unique IDs
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

# Decode

The following lines document a for loop that decodes the relevant rows
of `D_Charity.1.player.voiceBase64` and stores the result in
`../../data/wav/`.

``` r
# create filenames for the wav files that will be generated using a for loop
dt[D_Charity.1.player.voice_interface == 1,
   fileNames := paste0("../../data/wav/",
                       participant.code,
                       ".wav")]

# create a vector of "treated" participants to loop over
voiceInteractions <- dt[D_Charity.1.player.voice_interface == 1,
                        participant.code]

# run loop to decode and store corresponding files
for(id in voiceInteractions){
        dt[participant.code == id,
           base64decode(what = D_Charity.1.player.voiceBase64,
                        output = file(fileNames,
                                      "wb"))]
}
```

# Speech to Text

``` r
library(googleLanguageR)
```

    ## ✖ Failed! Auto-authentication via  GL_AUTH = ../../ibtanalytics-0ba5cc05ef54.json  - error was:   GL_AUTH specified in environment variables but file not found - 
    ## looked for ../../ibtanalytics-0ba5cc05ef54.json and called from /Users/haukeroggenkamp/dev/say-it-out-loud/analyses/pre-registered

``` r
gl_auth("../../../ibtanalytics-0ba5cc05ef54.json")
```

``` r
dt[, speech2text := as.character("")]

for(file in dt[!is.na(fileNames), fileNames]){
        tmp <- gl_speech(audio_source = file, 
                         languageCode = "en", 
                         encoding = "FLAC", 
                         sampleRateHertz = 44100, 
                         customConfig = list('audio_channel_count' = 1))
        
        transcript <- tmp$transcript[,1]
        
        dt[fileNames == file,
           # class(speech2text)]
           speech2text := transcript]
}

dt$speech2text
```

[^1]: According to the authors, `data.table` provides an enhanced
    version of `data.frame`s that reduce programming and compute time
    tremendously.

[^2]: Such as `D_Charity.1.player.voiceBase64`, for instance.

[^3]: This is the most recent data we have.

[^4]: I changed the columns’ order and truncated the long strings for
    illustrative purposes.
