from glob import iglob
import jyutping
import sys

non_han = '，。：'
multisyllable_allowlist = '兡瓸䇉竡尣兛瓩竏𥪕兝瓰竕嗧浬兞瓱竓呎吋啢𠺖兣糎甅竰卅𠯢兙瓧䇆竍卌'
invalidchar_list = ' 　！？；'

has_error = False
i = 0

for filename in iglob('*.csv'):
    with open(filename) as f:
        assert next(f).startswith('char,jyutping'), 'Invalid CSV header'

        for line_num, line in enumerate(f, 2):
            word, romans, *_ = line.rstrip('\n').split(',')

            word_ = [char for char in word if char not in non_han]
            romans_ = romans.split(' ')

            if '' in romans_:
                print(f'[{i:04}] \033[91m  ERROR: [{filename}:{line_num}] Leading, trailing or continuous spaces are not allowed: {word}, "{romans}"\033[0m', file=sys.stderr)
                has_error = True
                i += 1

            romans_ = [roman for roman in romans_ if roman]

            if len(word_) != len(romans_) and not any(char in multisyllable_allowlist for char in word):
                print(f'[{i:04}] WARNING: [{filename}:{line_num}] Length do not match: {word}, "{romans}"', file=sys.stderr)
                i += 1

            if any(char in invalidchar_list for char in word):
                print(f'[{i:04}] \033[91m  ERROR: [{filename}:{line_num}] Word contains invalid char: {word}, "{romans}"\033[0m', file=sys.stderr)
                has_error = True
                i += 1

            for char, roman in zip(word_, romans_):
                status = jyutping.validate(roman)
                if status == jyutping.ValidationStatus.UNCOMMON:
                    print(f'[{i:04}] WARNING: [{filename}:{line_num}] Uncommon jyutping "{roman}": {word}, "{romans}"', file=sys.stderr)
                    i += 1
                elif status == jyutping.ValidationStatus.INVALID:
                    print(f'[{i:04}] \033[91m  ERROR: [{filename}:{line_num}] Invalid jyutping "{roman}": {word}, "{romans}"\033[0m', file=sys.stderr)
                    has_error = True
                    i += 1

if has_error:
    sys.exit(1)
