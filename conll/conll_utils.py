#!/usr/bin/env python

import fileinput

def readInput():
    lines = []
    for line in fileinput.input():
        lines.append(line.strip())
    return lines


def getSentences(conll):
    sentence = []
    sentences = []
    for line in conll:
        if not line:
            sentences.append(sentence)
            sentence = []
        else:
            sentence.append(line)
    return sentences
