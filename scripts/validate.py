import sys
from glob import iglob
import jyutping

non_han = '，。：'
multisyllable_allowlist = '兡瓸䇉竡尣兛瓩竏𥪕兝瓰竕嗧浬兞瓱竓呎吋啢𠺖兣糎甅竰卅𠯢兙瓧䇆竍卌'

has_error = False
i = 0

for filename in iglob('*.csv'):
    with open(filename) as f:
        assert next(f).startswith('char,jyutping'), 'Invalid CSV header'

        for line_num, line in enumerate(f, 2):
            word, romans, *_ = line.rstrip('\n').split(',', 3)

            word_ = [char for char in word if char not in non_han]
            romans_ = romans.split(' ')

            if len(word_) != len(romans_):
                if any(char in multisyllable_allowlist for char in word):
                    continue

                print(f'[{i:04}] WARNING: File {filename} line {line_num}, length do not match: {word}, {romans}', file=sys.stderr)
                i += 1

            for char, roman in zip(word_, romans_):
                status = jyutping.validate(roman)
                if status == jyutping.ValidationStatus.UNCOMMON:
                    print(f'[{i:04}] WARNING: File {filename} line {line_num}, uncommon jyutping {roman}: {word}, {romans}', file=sys.stderr)
                    i += 1
                elif status == jyutping.ValidationStatus.INVALID:
                    print(f'[{i:04}] \033[91mERROR: File {filename} line {line_num}, invalid jyutping {roman}: {word}, {romans}\033[0m', file=sys.stderr)
                    has_error = True
                    i += 1

# assert not has_error, 'The file should not contain errors'
