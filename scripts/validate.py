import jyutping
import sys
from glob import iglob

non_han = {*'，：'}
multisyllable_allowlist = {*'兡瓸䇉竡尣兛瓩竏𥪕兝瓰竕嗧浬兞瓱竓呎吋啢𠺖兣糎甅竰卅𠯢兙瓧䇆竍卌'}

with open('scripts/ignore.csv', encoding='utf-8') as f:
    next(f)
    ignoreroman_list = {tuple(line.rstrip('\n').split(',')) for line in f}

def is_han(char):
    return char == '\u3007' or \
           '\u3400' <= char <= '\u4dbf' or \
           '\u4e00' <= char <= '\u9fff' or \
           '\uf900' <= char <= '\ufaff' or \
           '\U00020000' <= char <= '\U0002a6df' or \
           '\U0002a700' <= char <= '\U0002ebef' or \
           '\U0002f800' <= char <= '\U0002fa1f' or \
           '\U00030000' <= char <= '\U000323af'

has_error = False
i = 0

for filename in iglob('*.csv'):
    with open(filename, encoding='utf-8') as f:
        if not next(f).startswith('char,jyutping'):
            continue

        for line_num, line in enumerate(f, 2):
            word, romans, *_ = line.rstrip('\n').split(',')

            word_ = [char for char in word if char not in non_han]
            romans_ = romans.split(' ')

            if '' in romans_:
                print(f'[{i:04}] \033[91m  ERROR: [{filename}:{line_num}] Leading, trailing or continuous spaces are not allowed: {word}, "{romans}"\033[0m', file=sys.stderr)
                has_error = True
                i += 1

            romans_ = [roman for roman in romans_ if roman]

            if len(word_) != len(romans_) and not any(char in multisyllable_allowlist for char in word_):
                print(f'[{i:04}] \033[91m  ERROR: [{filename}:{line_num}] Length do not match: {word}, "{romans}"\033[0m', file=sys.stderr)
                has_error = True
                i += 1

            if not all(is_han(char) for char in word_):
                print(f'[{i:04}] \033[91m  ERROR: [{filename}:{line_num}] Word contains invalid char: {word}, "{romans}"\033[0m', file=sys.stderr)
                has_error = True
                i += 1

            for char, roman in zip(word_, romans_):
                if (char, roman) in ignoreroman_list:
                    continue
                status = jyutping.validate(roman, jyutping.TestSet.LOOSE)
                if status == jyutping.ValidationStatus.UNCOMMON:
                    print(f'[{i:04}] WARNING: [{filename}:{line_num}] Uncommon jyutping "{roman}": {word}, "{romans}"', file=sys.stderr)
                    i += 1
                elif status == jyutping.ValidationStatus.INVALID:
                    print(f'[{i:04}] \033[91m  ERROR: [{filename}:{line_num}] Invalid jyutping "{roman}": {word}, "{romans}"\033[0m', file=sys.stderr)
                    has_error = True
                    i += 1

if has_error:
    sys.exit(1)
