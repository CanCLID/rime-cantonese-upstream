from glob import iglob
import jyutping
import re
import sys
from itertools import zip_longest, accumulate

non_han = {*'，：'}
other_han = {*'\u3006\ufa0e\ufa0f\ufa11\ufa13\ufa14\ufa1f\ufa21\ufa23\ufa24\ufa27\ufa28\ufa29'}
multisyllable_allowlist = {*'兡瓸䇉竡尣兛瓩竏𥪕兝瓰竕嗧浬兞瓱竓呎吋啢𠺖兣糎甅竰卅𠯢兙瓧䇆竍卌'}

with open('scripts/ignore.csv', encoding='utf-8') as f:
    next(f)
    ignoreroman_list = set(map(lambda line: tuple(line.rstrip('\n').split(',')), f))

def is_unified_ideograph(char):
    return '\u4e00' <= char <= '\u9fff' or \
           '\u3400' <= char <= '\u4dbf' or \
           '\U00020000' <= char <= '\U0002a6df' or \
           '\U0002a700' <= char <= '\U0002ebef' or \
           '\U00030000' <= char <= '\U000323af' or \
           char in other_han

def get_additional_information(char):
    return ': Radicals' if '\u2e80' <= char <= '\u2fef' else \
           ': Symbols and Punctuation' if '\u3000' <= char <= '\u303f' else \
           ': Strokes' if '\u31c0' <= char <= '\u31ef' else \
           ': Compatibility Ideographs' if '\uf900' <= char <= '\ufaff' else \
           ': Compatibility Ideographs Supplement' if '\U0002f800' <= char <= '\U0002fa1f' else \
           ''

def utf16_byte_length(char):
    return (char >= '\U00010000') + 1

for filename in sys.argv[1:] or iglob('*.csv'):
    with open(filename, encoding='utf-8') as f:
        first_line = next(f)
        if not first_line.startswith('char,jyutping'):
            print(f'ERROR: [{filename}:1:1,{sum(map(utf16_byte_length, first_line)) + 1}] Invalid CSV header')

        for line_num, line in enumerate(f, 2):
            def error(start, end, message):
                # nonlocal filename, line
                print(f'ERROR: [{filename}:{line_num}:{utf16_column_mapper[start]},{utf16_column_mapper[end]}] {message}')

            def warn(start, end, message):
                # nonlocal filename, line
                print(f'WARNING: [{filename}:{line_num}:{utf16_column_mapper[start]},{utf16_column_mapper[end]}] {message}')

            def yieldChars(chars):
                s = ''
                isLeading = True
                for i, char in enumerate(chars):
                    if char in non_han:
                        s += char
                    else:
                        if s:
                            if isLeading:
                                error(i - len(s), i, "Leading punctuation is not allowed")
                            elif len(s) > 1:
                                error(i - len(s), i, "Continuous punctuation is not allowed")
                            s = ''
                        isLeading = False
                        yield (i, char)
                if s:
                    i += 1
                    error(i - len(s), i, "Trailing punctuation is not allowed")

            def yieldRomans(romans, start):
                s = ''
                isSpace = True
                isLeading = True
                for i, roman in enumerate(romans, start):
                    if (roman == ' ') != isSpace:
                        if s:
                            if isSpace:
                                if isLeading:
                                    error(i - len(s), i, "Leading space is not allowed")
                                elif len(s) > 1:
                                    error(i - len(s), i, "Continuous spaces are not allowed")
                            else:
                                yield (i, s)
                            s = ''
                        isSpace = not isSpace
                        isLeading = False
                    s += roman
                if s:
                    i += 1
                    if isSpace:
                        error(i - len(s), i, "Trailing space is not allowed")
                    else:
                        yield (i, s)

            utf16_column_mapper = list(accumulate(map(utf16_byte_length, line), initial=1))
            columns = line.rstrip('\n').split(',')
            if len(columns) < 2:
                error(0, len(line), 'Invalid line')
                continue
            chars, romans, *_ = columns

            length_mismatch = False
            for (char_i, char), (roman_i, roman) in zip_longest(yieldChars(chars), yieldRomans(romans, len(chars) + 1), fillvalue=(None, None)):
                if length_mismatch is not None and (not char or not roman):
                    length_mismatch = True
                if char:
                    if char in multisyllable_allowlist:
                        length_mismatch = None
                    if not is_unified_ideograph(char):
                        error(char_i, char_i + 1, f'Invalid character "{char}"{get_additional_information(char)}')
                if roman and (char, roman) not in ignoreroman_list:
                    status = jyutping.validate(roman)
                    if status == jyutping.ValidationStatus.UNCOMMON:
                        warn(roman_i - len(roman), roman_i, f'Uncommon jyutping: "{roman}"')
                    elif status == jyutping.ValidationStatus.INVALID:
                        error(roman_i - len(roman), roman_i, f'Invalid jyutping: "{roman}"')

            if length_mismatch:
                warn(0, len(line), 'Length does not match')
