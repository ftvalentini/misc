#!/bin/bash
# 
# Clean a corpus of text (one document per line) to train static word 
# embeddings. Removes non-ascii characters, lowercases, removes punctuation 
# except for the apostrophes of contractions and possessive 's. Tokens are 
# words, contractions (except n't is not a separate token), and the possessive 
# 's. For example, "he's" is separated into "he" and "'s", but "don't" is kept
# as "don't".
# 
# NOTES:
#   - TRANSLIT is important to remove accents (eg. á -> a).
#   - All non-alphanumeric characters are replaced with a single space except 
#     for dash (-) and apostrophe (')
#   - Numbers are separated into tokens (eg. "20,000.00" -> "20000 00") 
#   - There might be some remaining dashes (-) and apostrophes (') in the 
#     output of weird documents
#   - Acronyms are supposed to be kept w/out trailing dot (eg. "U.S.A." -> "u.s.a.")
#     This is done with a weird workaround because sed doesn't support lookahead. 
# 
# Inspired by:
# https://chrisculy.net/lx/wordvectors/dist_freq_intro.html#Preprocessing


iconv -c -f utf8 -t ascii//TRANSLIT $1 | # removes non ascii characters 
    tr '[:upper:]' '[:lower:]' | # replace caps with low
    sed -E "s/--/ -- /g" | # replace — (utf8) with -- (ascii) between spaces
    sed -E "s/([0-9]*),([0-9]*)/\1\2/g" | # remove commas in comma-separated digits
    sed -E "s/([[:alpha:]])\.([[:alpha:]])\./\1'-'-\2'-'-/g" | # replace dots in acronyms with adhoc combo of ' and -
    sed -E "s/[^'a-z0-9\-]+/ /g" | # remove all non-alphanumeric except for ' and -
    sed -E "s/([[:alpha:]])'\-'\-([[:alpha:]])'\-'\-/\1\.\2./g" | # convert acronyms back to dots
    sed -E "s/ ['-]/ /g" | # replace useless remaining ' and -
    sed -E "s/['-] / /g" | 
    sed -E "s/^['-]//g" |
    sed -E "s/['-]$//g" | 
    sed -E "s/'v/ 'v/g" | # separate English contractions and possessives
    sed -E "s/'ll/ 'll/g" |
    sed -E "s/'s/ 's/g" |
    sed -E "s/'d/ 'd/g" |
    sed -E "s/i'm/i 'm/g" |
    sed -E "s/'re/ 're/g" |
    tr -s "[:blank:]" | # remove multiple whitespace
    sed "s/^[[:blank:]]*//; s/[[:blank:]]*$//; /^$/d" # remove leading and trailing whitespace & empty lines
    # the last 2 steps might be unnecessary


    # sed "s/^[ \t]*//; s/[ \t]*$//; /^$/d" # remove leading and trailing whitespace & empty lines
    # sed "s/^[ \t]*//;s/[ \t]*$//" # remove leading and trailing whitespace
    # sed "s/^ *//; s/ *$//" # remove empty lines and extra whitespace
    # sed -E "s/\.+/\./g" | # replace multiple dots with a single dot 
    # sed -E "s/(^\.|\.$)//g" | # remove trailing dots and leading dots 
    # sed -E "s/ \. / /g" # remove dots between whitespace


# NOTE esta version de hyperwords (levy y goldberg) 
# https://github.com/BIU-NLP/hyperwords/blob/master/scripts/clean_corpus.sh
# no me convence porque no separa las contracciones como he's, don't, David's, they're, etc.
