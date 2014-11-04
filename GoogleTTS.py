#!/usr/bin/python

import argparse
import codecs
import sys
import time
import urllib.parse
import urllib.request
import urllib.response
import urllib.error

BOMS = (
    (codecs.BOM_UTF8, "utf-8"),
    (codecs.BOM_UTF32_BE, "utf-32-be"),
    (codecs.BOM_UTF32_LE, "utf-32-le"),
    (codecs.BOM_UTF16_BE, "utf-16-be"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),
)

DEFAULT_ENCODING = "utf-8"

def getEncodingFromBom(data):
    '''
    Get the name of the encoding from the BOM.
    Returns tuple of
        (name of detected encoding,
        data with encoding stripped off)
    http://unicodebook.readthedocs.org/guess_encoding.html
    '''
    dataBytes = data.encode()

    for bom, encoding in BOMS:
        if dataBytes.startswith(bom):
            #print("Detected file encoding from BOM %s" % (encoding,))
            # Slice off BOM
            return (encoding, data[1:])

    #print("Could not detect BOM")
    return (None, data)

def convertFile(fileName,
    newlineDelimiter,
    wordDelimiter,
    language,
    language1,
    language2,
    encoding):

    fileData = open(fileName, encoding=encoding, mode='r')
    rawText = fileData.read()
    fileData.close()

    # Get BOM
    (detectedEncoding, text) = getEncodingFromBom(rawText)
    if (detectedEncoding is not None and
        detectedEncoding != encoding):

        print("Warning: expected encoding %s, but file BOM is %s" %
            (encoding, detectedEncoding))

        encoding = detectedEncoding
    
    textString = text
    textString = textString.lower()

    # Weekly words list is a
    # string of the format "English Russian, English Russian .."
    # - write word pairs to csv
    # - get TTS for Russian
    wordPairs = textString.split(newlineDelimiter)
    if len(wordPairs) > 1:

        textString = ""
        csvText = ""

        for wordPair in wordPairs:
            language1Word = None
            language2Word = None
            if not language2:
                language1Word = wordPair.strip()
            else:
                (language1Word, sep, language2Word) = \
                    wordPair.rpartition(wordDelimiter)
                language1Word = language1Word.strip()
                language2Word = language2Word.strip()
            
            # Ignore blank lines
            csvWordDelimiter = "\t"
            csvNewlineDelimiter = "\n"
            if language1Word and (not language2 or language2Word):
                if language2Word:
                    csvText = csvText + language2Word + csvWordDelimiter
                csvText = csvText + language1Word
                csvText = csvText + csvNewlineDelimiter

                if language == language1:
                    textString = textString + language1Word + "\n"
                elif language == language2:
                    textString = textString + language2Word + "\n"

        outCsvName = "out.csv"
        print("Writing to", outCsvName)
        try:
            outFile = open(outCsvName, encoding=encoding, mode="w")
            outFile.write(csvText)
            outFile.close()
        except IOError as e:
            print(repr(e))

    # Text in the form of "Russian\nRussian\nRussian"
    lines = textString.splitlines()
    wordNumber = 1
    for word in lines:
        convertWord(language, encoding, word, str(wordNumber))
        wordNumber = wordNumber + 1
        time.sleep(0.5)

def convertWord(language, encoding, word, wordNumber=""):

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

    outputFileName = wordNumber + word + ".mp3"

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
        #print("Requesting", mp3url)

        response = urllib.request.urlopen(requestData)
        responseData = response.read()

        file = open(outputFileName, 'wb')
        file.write(responseData)
        file.close()
        try:
            print('Saved MP3 to %s' %
            (outputFileName.encode(encoding, errors="replace"),))
        except UnicodeEncodeError as e:
            print('Saved MP3 to %s' % (e,))

    except urllib.error.HTTPError as e:
        print("Error making request", str(e))

def main():
    description='Google TTS Word Generator'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-l','--language', 
        action='store', 
        nargs='?',
        help='Language for which to generate TTS (eg. "en").',
        default='en')

    parser.add_argument('-l1','--language1', 
        action='store', 
        nargs='?',
        help='1st language of the input text (eg. "en").')

    parser.add_argument('-l2','--language2', 
        action='store', 
        nargs='?',
        help='2nd language of the input text (eg. "en").')


    parser.add_argument('-e','--encoding', 
        action='store', 
        nargs='?',
        help='Encoding of the input text (eg. "ascii", "utf-8").',
        default=DEFAULT_ENCODING)

    parser.add_argument('-nd', '--newlinedelimiter',
        action='store',
        nargs='?',
        help='Separator between newlines in file. (eg. "\n")',
        default='\n')
    parser.add_argument('-wd', '--worddelimiter',
        action='store',
        nargs='?',
        help='Separator between words in file. (eg. ",", "\t")',
        default=',')


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
        # Convert escaped character such as "\t", "\n" to real tabs, newlines
        unicodeDelimiter = args.newlinedelimiter.encode()
        newlineDelimiter = unicodeDelimiter.decode('unicode_escape')

        unicodeDelimiter = args.worddelimiter.encode()
        wordDelimiter = unicodeDelimiter.decode('unicode_escape')

        # Decide on input languages if not given
        language1 = args.language1
        if not language1:
            language1 = args.language

        # Language 2 can be None

        convertFile(args.file,
            newlineDelimiter,
            wordDelimiter,
            args.language,
            args.language1,
            args.language2,
            args.encoding)

    elif args.string:
        word = ' '.join(map(str,args.string))
        convertWord(args.language, args.encoding, word)

if __name__ == "__main__":
    main()

