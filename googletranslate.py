#!/usr/bin/env python

# Juneki Hong juneki@jhu.edu 
# January 2014

# I found a bash script in the comments section of this page:
# http://www.howtoforge.com/using-google-translate-from-the-command-line
# I adapted this script to python

import subprocess
import pycurl
import StringIO
import argparse
import sys

# Set up pycurl. 
# Example taken from http://pycurl.sourceforge.net/doc/curlobject.html
curl = pycurl.Curl()
curl.setopt(pycurl.URL, "http://www.google.com")
curl.setopt(pycurl.HTTPHEADER, ["Accept:"])

# Set up a string that can store the response HTML
string = StringIO.StringIO()
curl.setopt(pycurl.WRITEFUNCTION, string.write)

# Some more curl options. They are probably optional.
curl.setopt(pycurl.FOLLOWLOCATION, 1)
curl.setopt(pycurl.MAXREDIRS, 5)

try:
    curl.perform()

except pycurl.error:
    sys.stderr.write("No internet connection. Aborting.")
    exit()


def printLanguageOptions(curl):
    URL = "http://translate.google.com/m?&mui=sl"
    curl.setopt(pycurl.URL, URL)
    curl.perform()
    HTML = string.getvalue()
    languages = []
    
    index = HTML.find("m?sl=")
    while index != -1:
        HTML = HTML[index+len("m?sl="):]
        index2 = HTML.find("</a>")
        languages.append(HTML[:index2])
        index = HTML.find("m?sl=")
        
    for i in xrange(len(languages)):        
        languages[i] = languages[i].split("\">")
        languages[i] = languages[i][0] + " -> " + languages[i][1]

    print languages[0]
    languages = languages[1:]
    flattabs(languages, 5)


def flattabs(l, cols=4, padding=25):
    mod = len(l) % cols
    if mod != 0:
        diff = cols - mod
        for i in xrange(diff):
            l.append("")

    split = len(l)/cols
    temp = l
    lists = []

    for x in xrange(cols):
        lists.append(temp[:split])
        temp = temp[split:]
        
    for i in xrange(len(lists[0])):
        for x in xrange(len(lists)):
            sys.stdout.write(("{0:<"+str(padding)+"s}").format(lists[x][i]))
        print


# Command line arguments
usageString = sys.argv[0] + " [options] [source language] [target language] [sentence]"

parser = argparse.ArgumentParser(description='Call Google Translate from the command line.', usage=usageString, add_help=False)
parser.add_argument("-v", "--verbose", dest='verbose', default=True, action="store_true",
                    help='Prints out extra things that may help helpfullness, and readably. (On by default)')
parser.add_argument("-s", "--silent", dest="silent", default=False, action="store_true",
                    help="Suppresses the extra print statements. Only prints out the results.")
parser.add_argument("-f", "--filein", dest="filename", default=None, 
                    help="Specify a file to read from")
parser.add_argument("-b", "--browser", dest="browser", default=False, action="store_true",
                    help="Opens up your default browser instead of a command line output")
parser.add_argument("-h", "--help", dest="helpFlag", default=False, action="store_true", 
                    help="show this message and exit.")
parser.add_argument('strings', nargs='*')

args = parser.parse_args()


def printHelp(parser):
    parser.print_help()

    print
    print "example:"
    print sys.argv[0]+" en pl how"
    print sys.argv[0]+" en pl \"Mary had a little lamb\""
    print

    print "Available languages:"
    print "---------------------"

    printLanguageOptions(curl)
    exit()


if args.helpFlag:
    printHelp(parser)

try:
    FROM = args.strings[0]
    TO = args.strings[1]
    if (args.filename):
        f = open(args.filename)
        f = f.readlines()
        SENTENCE = " ".join(f).split()
    else:
        SENTENCE = args.strings[2:]
    SENTENCE = "+".join(SENTENCE)
except IndexError:
    try:
        FROM = "auto"
        TO = "en"
        SENTENCE = args.strings[0:]
        SENTENCE = "+".join(SENTENCE)
    except IndexError:
        printHelp(parser)

# We need to change exchange all the whitespaces in the SENTENCE to "+"
SENTENCE = SENTENCE.replace(" ", "+")


if (args.verbose and not args.silent):
    print FROM, "--->", TO

if (args.browser):
    URL = "http://translate.google.com/#"+FROM+"/"+TO+"/"+SENTENCE    
    call(["google-chrome", URL])
else:
    URL = "https://translate.google.com/m?hl=en&sl="+FROM+"&tl="+TO+"&ie=UTF-8&prev=_m&q="+SENTENCE


    #print URL
    #print "https://translate.google.com/m?hl=en&sl=auto&tl=pl&ie=UTF-8&prev=_m&q=Mary+had+a+little+lamb"


    # Enviornment call out to curl.
    curl = subprocess.Popen(["curl", "-s", "--user-agent", "Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.34 (KHTML, like Gecko) QupZilla/1.3.1 Safari/534.34", URL], stdout=subprocess.PIPE)    

    sed = subprocess.Popen(["sed", "-n", "s/.*class=\"t0\">//;s/<.*$//p"], stdin=curl.stdout, stdout=subprocess.PIPE)
    curl.stdout.close()
    output,err = sed.communicate()

    print output


# Using python for the curl command was pretty frustrating because of how it handled Unicode
# Unicode characters would always get mangled when I tried to print out the result.
# After a while I gave up and resorted to an enviornment call out to curl.
"""curl.setopt(pycurl.URL, URL)
curl.perform()

HTML =  string.getvalue()
index = HTML.find("class=\"t0\">")
HTML = HTML[index+len("class=\"t0\">"):]
index2 = HTML.find("</div>")
HTML = HTML[:index2]

print HTML
"""
