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

esc = False
gens = []   # list of generators
user_charsets = []
options, args = getopt.getopt(sys.argv[1:], '1:2:3:4:5:6:7:8:9:')
user_charsets = [tuple(sorted(set(arg))) for opt, arg in options]

# This works by generating a list of generators, for each character position,
# such that [<generator1>, <generator2, ...] is then fed to itertools.product()
# to create the wordlist.

for c in args[0]:
    if not esc and c == '?':
        esc = True
    else:
        if esc:
            if c == '?': gens.append((a for a in '?'))
            elif c == 'a': gens.append((a for a in string.ascii_lowercase))
            elif c == 'A': gens.append((a for a in string.ascii_uppercase))
            elif c == '0': gens.append((a for a in string.digits))
            elif c == '.': gens.append((a for a in string.punctuation))
            elif c == 'x': gens.append((a for a in set(string.hexdigits.lower())))
            # Handle user character sets -1 through -9
            elif c in string.digits: gens.append((a for a in user_charsets[int(c)-1]))
        else:
            gens.append((a for a in c))
        esc = False

for word in map(''.join, product(*gens)):
    print(word)
