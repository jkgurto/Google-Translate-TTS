Google Translate TTS WordList
====================

A modified version of
[hungtruong/Google-Translate-TTS]
(https://github.com/hungtruong/Google-Translate-TTS)
which can take a newline separated list of words.

```
usage: GoogleTTS.py [-h] [-l [LANGUAGE]] [-e [ENCODING]]
                    (-f FILE | -s STRING [STRING ...])

Google TTS Word Generator

optional arguments:
  -h, --help            show this help message and exit
  -l [LANGUAGE], --language [LANGUAGE]
                        Language of the output text (eg. "en").
  -e [ENCODING], --encoding [ENCODING]
                        Encoding of the input text (eg. "ascii", "utf-8").
  -f FILE, --file FILE  File to read text from.
  -s STRING [STRING ...], --string STRING [STRING ...]
                        A string of text to convert to speech.
```


Examples
===================

To convert a list of words, separated by newlines from a file:

```
GoogleTTS.py -l ru -e utf-8 -f test.csv
```

To convert text from the command line to a file:

```
GoogleTTS.py -l en -e ascii -s hello
```
