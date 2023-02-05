from glob import iglob
from operator import itemgetter
from itertools import accumulate
from collections import defaultdict

non_han = {*'，： '}

def is_ascii_lowercase_letter(char):
    return 'a' <= char <= 'z'

def is_ascii_letter(char):
    return 'A' <= char <= 'Z' or 'a' <= char <= 'z'

def column_start(column):
    return len(column) + 1

listed = set()
for filename in ['char.csv', 'scripts/ignore.csv']:
    with open(filename, encoding='utf-8') as f:
        assert next(f).startswith('char,jyutping')
        listed |= {tuple(line.rstrip('\n').split(',')[:1]) for line in f}

unlisted = defaultdict(list)
for filename in iglob("*.csv"):
    if filename == 'char.csv':
        continue
    with open(filename, encoding='utf-8') as f:
        column_names = next(f).rstrip('\n').split(',')
        if "char" not in column_names or "jyutping" not in column_names:
            continue
        chars_column_index = column_names.index("char")
        romans_column_index = column_names.index("jyutping")

        for line_num, line in enumerate(f, 2):
            def yield_chars(chars, start):
                s = ''
                is_punctuation = True
                for i, char in enumerate(chars, start):
                    if (char in non_han) != is_punctuation:
                        if s:
                            if not is_punctuation:
                                yield (i, s)
                            s = ''
                        is_punctuation = not is_punctuation
                    if not is_punctuation and s and not (is_ascii_lowercase_letter(char) and is_ascii_letter(s[-1])):
                        yield (i, s)
                        s = ''
                    s += char
                if s:
                    i += 1
                    if not is_punctuation:
                        yield (i, s)

            def yield_romans(romans, start):
                s = ''
                is_space = True
                for i, roman in enumerate(romans, start):
                    if (roman == ' ') != is_space:
                        if s:
                            if not is_space:
                                yield (i, s)
                            s = ''
                        is_space = not is_space
                    s += roman
                if s:
                    i += 1
                    if not is_space:
                        yield (i, s)

            columns = line.rstrip('\n').split(',')
            columns_start = list(accumulate(map(column_start, columns), initial=0))

            if chars_column_index < len(columns) > romans_column_index:
                chars_orig = columns[chars_column_index]
                romans_orig = columns[romans_column_index]
                chars = yield_chars(chars_orig, columns_start[chars_column_index])
                romans = yield_romans(romans_orig, columns_start[romans_column_index])
                for char_i, char in chars:
                    try:
                        roman_i, roman = next(romans)
                    except StopIteration:
                        break
                    if (char, roman) not in listed:
                        unlisted[(char, roman)].append(f'{filename}:{line_num}')

with open('scripts/unlisted.csv', 'w', encoding='utf-8') as f:
    print('char', 'jyutping', 'location', sep=',', file=f)
    for (char, roman), locations in sorted(unlisted.items(), key=itemgetter(0)):
        print(char, roman, ';'.join(locations), sep=',', file=f)
