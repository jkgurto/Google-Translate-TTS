#!/usr/bin/python

import sys
import argparse
import urllib.parse
import urllib.request
import urllib.response
import urllib.error
import time

def convertFile(fileName, language, encoding):

    fileData = open(fileName, encoding=encoding, mode='r')
    text = fileData.read()
    fileData.close()

    lines = text.splitlines()
    for word in lines:
        convertWord(language, encoding, word)
        time.sleep(0.5)

def convertWord(language, encoding, word):

    wordLen = len(word)
    if wordLen == 0:
        print("Word has no length")
        return
    elif wordLen > 100:
        print("Word is more than 100 characters")
        return

    try:
        quotedWord = urllib.parse.quote(word, encoding=encoding)
    except urllib.error.UnicodeEncodeError as e:
        print("Error quoting string", str(e))
        return

    outputFileName = word + ".mp3"
    print('Saved MP3 to %s' % outputFileName.encode(encoding))

    # Eg.
    # http://translate.google.com/translate_tts?tl=en&q=hello&total=5&idx=0
    idx = 0
    mp3url =\
"http://translate.google.com/\
translate_tts?tl=%s&q=%s&total=%s&idx=%s" % \
        (language, quotedWord, wordLen, idx)

    # Pretend to be human
    headers = {
        "Host":"translate.google.com",
        "Referer":"http://www.gstatic.com/translate/sound_player2.swf",
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) \
AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.163 Safari/535.19"
    }

    requestData = urllib.request.Request(mp3url, None, headers)

    try:
        print("Requesting", mp3url)

        response = urllib.request.urlopen(requestData)
        responseData = response.read()

        file = open(outputFileName, 'wb')
        file.write(responseData)
        file.close()
        print('Saved MP3 to %s' % outputFileName.encode(encoding))

    except urllib.error.HTTPError as e:
        print("Error making request", str(e))

def main():
    description='Google TTS Word Generator'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-l','--language', 
        action='store', 
        nargs='?',
        help='Language of the output text (eg. "en").',
        default='en')

    parser.add_argument('-e','--encoding', 
        action='store', 
        nargs='?',
        help='Encoding of the input text (eg. "ascii", "utf-8").',
        default='ascii')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f','--file',
        help='File to read text from.')
    group.add_argument('-s', '--string',
        action='store',
        nargs='+',
        help='A string of text to convert to speech.')

    if len(sys.argv)==1:
       parser.print_help()
       sys.exit(1)

    args = parser.parse_args()
    if args.file:
        convertFile(args.file, args.language, args.encoding)

    elif args.string:
        word = ' '.join(map(str,args.string))
        convertWord(args.language, args.encoding, word)

if __name__ == "__main__":
    main()

