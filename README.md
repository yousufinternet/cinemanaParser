# cinemanaParser

A simple script the scraps the cinemana website and downloads tv-series and movies

## Requirements

needs `aria2` to download podcasts, you can get it from [here](https://aria2.github.io/). it has to be in PATH.

needs beautifulsoup to parse webpages `pip install beautifulsoup4`

## Usage

```
cinemana_parser.py [-h] [--movie] [--no-subtitle] [--pick-res]
[--res RES] [--season CUSTOM_SEASONS]
[--concurrent-downloads CONCURRENT_DOWNLOADS]
URLs [URLs ...]

Provided a movie or a tv-series url on cinemana gives you the option to
download the movie with subtitle files or download all or some episodes

positional arguments:
URLs                  one or more cinemana urls

optional arguments:
-h, --help            show this help message and exit
--movie               Add this flag if you are downloading a movie or you
want to only download a single episode, by default the
this option is off
--no-subtitle         If you don't want the subtitles downloaded
--pick-res            Add this flag if you want to pick a resolution from
the available resolutions (note that this means you
have to pick a resolution for each episode)
--res RES
--season CUSTOM_SEASONS
specify the season number you want to download, repeat
for more than one
--concurrent-downloads CONCURRENT_DOWNLOADS
pass concurrent downloads option to aria2c
```
