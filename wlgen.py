#!/usr/bin/env python
#
# Hashcat-like wordlist generator.
# Usage: ./wlgen.py [-1 charset1 -2 ... -9 charset9] pattern > dict.txt
# Patterns recognized:
# ?a = lowercase alpha ascii
# ?A = uppercase alpha ascii
# ?0 = digits 0-9
# ?. = punctuation symbols
# ?x = lowercase hex digits
# ?1 through ?9 = user character sets
#
# Copyright (c) 2020, Alexandre Hamelin <alexandre.hamelin gmail.com>
# Licensed under the MIT License

import sys
import string
import getopt
from itertools import product

# This works by generating a list of generators, for each character position,
# such that [<generator1>, <generator2, ...] is then fed to itertools.product()
# to create the wordlist.

def translate_charset(code, custom_charsets=[]):
    classes = {
        '?' : '?',
        'a' : string.ascii_lowercase,
        'A' : string.ascii_uppercase,
        '0' : string.digits,
        '.' : string.punctuation,
        'x' : '012345678abcdef',
        'X' : '012345678ABCDEF',
    }
    return classes.get(code, None)


def parse_pattern(pattern, options, custom=True):
    charset_list = []   # list of possible character sets for each position
    esc = False
    for c in pattern:
        if not esc and c == '?':
            esc = True
            continue
        if esc:
            charset = translate_charset(c)
            if charset:
                charset_list.append(charset)
            # Handle user character sets -1 through -9
            elif custom and c in '123456789':
                charset_pattern = options['user_charsets'][c]
                # Expand the pattern to recognize built-in charsets.
                # Remove duplicates and flatten the lists to a string.
                expanded_charset = ''.join(sorted(set(
                    map(lambda p: ''.join(str(e) for e in iter(p)),
                        parse_pattern(charset_pattern, options, False))
                )))
                charset_list.append(expanded_charset)
        else:
            charset_list.append(c)
        esc = False
    return charset_list

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], '1:2:3:4:5:6:7:8:9:i:')
    options = {
        'user_charsets' : {},
        'input_file' : None,
    }
    for opt, arg in opts:
        if opt[1] in string.digits: options['user_charsets'][opt[1]] = arg
        elif opt == '-i': options['input_file'] = arg

    patterns = args
    if options['input_file']:
        with open(options['input_file'], 'r') as inputfile:
            patterns = inputfile.read().splitlines()

    for p in patterns:
        charsets = parse_pattern(p, options)
        for word in map(''.join, product(*charsets)):
            print(word)
