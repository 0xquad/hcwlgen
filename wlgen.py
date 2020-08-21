#!/usr/bin/env python
#
# Hashcat-like wordlist generator.
# Usage: ./wlgen.py [-1 charset1 -2 ... -9 charset9] [-H] [pattern|-i file]
# Built-in character sets:
# ?a = lowercase alpha ascii
# ?A = uppercase alpha ascii
# ?0 = digits 0-9
# ?. = punctuation symbols
# ?x = lowercase hex digits
# ?X = uppercase hex digits
# ?1 through ?9 = user character sets
# Hashcat pattern format can be used instead with the -H option (except ?b).
# Built-in charsets can be specified in user character sets too.
#
# Copyright (c) 2020, Alexandre Hamelin <alexandre.hamelin gmail.com>
# Licensed under the MIT License

import sys
import string
import getopt
from itertools import product

# This works by generating a list of iterables, for each character position,
# such that [<iterable1>, <iterable2>, ...] is then fed to itertools.product()
# to create the wordlist.

def translate_charset(code, options):
    hc = options['hashcat_fmt']
    classes = {
        '?' : '?',
        'l' if hc else 'a' : string.ascii_lowercase,
        'u' if hc else 'A' : string.ascii_uppercase,
        'd' if hc else '0' : string.digits,
        's' if hc else '.' : ' ' + string.punctuation if hc else string.punctuation,
        'h' if hc else 'x' : string.digits + 'abcdef',
        'H' if hc else 'X' : string.digits + 'ABCDEF',
    }
    if hc:
        classes['a'] = classes['l'] + classes['u'] + classes['d'] + classes['s']
    return classes.get(code, None)


def parse_pattern(pattern, options, custom=True):
    charset_list = []   # list of possible character sets for each position
    esc = False
    for c in pattern:
        if not esc and c == '?':
            esc = True
            continue
        if esc:
            charset = translate_charset(c, options)
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


def generate_dict(patterns, options):
    for p in patterns:
        charsets = parse_pattern(p, options)
        yield from map(''.join, product(*charsets))


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], '1:2:3:4:5:6:7:8:9:i:H')
    options = {
        'user_charsets' : {},
        'input_file' : None,
        'hashcat_fmt' : False,
    }
    for opt, arg in opts:
        if opt[1] in string.digits: options['user_charsets'][opt[1]] = arg
        elif opt == '-i': options['input_file'] = arg
        elif opt == '-H': options['hashcat_fmt'] = True

    patterns = args
    if options['input_file']:
        with open(options['input_file'], 'r') as inputfile:
            patterns = inputfile.read().splitlines()
            for line in patterns[:]:
                if line[0] in '123456789' and line[1] == '=':
                    options['user_charsets'][line[0]] = line[2:]
                    patterns.remove(line)

    for word in generate_dict(patterns, options):
        print(word)
