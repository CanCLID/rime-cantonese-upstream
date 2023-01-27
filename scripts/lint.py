import jyutping
import time
from glob import iglob
from os.path import basename
from itertools import zip_longest, accumulate
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

non_han = {*'，：'}
other_han = {*'〇﨎﨏﨑﨓﨔﨟﨡﨣﨤﨧﨨﨩'}
multisyllable_allowlist = {*'兡瓸䇉竡尣兛瓩竏𥪕兝瓰竕嗧浬兞瓱竓呎吋啢𠺖兣糎甅竰卅𠯢兙瓧䇆竍卌'}
other_column_values = {
    "pron_rank": {"預設", "常用", "罕見", "棄用"},
    "tone_var": {"", "本調", "變調"},
    "literary_vernacular": {"", "文讀", "白讀"},
}

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

cache = {}
headers = {}
curr_messages = {}

def lint(filename):
    with open(filename, encoding='utf-8') as f:
        new_messages = []

        first_line = next(f, "")
        if not first_line.startswith('char,jyutping'):
            new_messages.append(f'{filename}:1:1,{sum(map(utf16_byte_length, first_line)) + 1}: ERROR: Invalid CSV header')
        other_column_names = first_line.rstrip('\n').split(',')[2:]

        if first_line != headers.get(filename):
            cache[filename] = {}

        for line_num, line in enumerate(f, 2):
            if line in cache[filename]:
                new_messages += map(lambda line: f'{filename}:{line_num}:{line}', cache[filename][line])
                continue
            messages = []

            def error(start, end, message):
                messages.append(f'{utf16_column_mapper[start]},{utf16_column_mapper[end]}: ERROR: {message}')

            def warn(start, end, message):
                messages.append(f'{utf16_column_mapper[start]},{utf16_column_mapper[end]}: WARNING: {message}')

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
            chars, romans, *other_columns = columns

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

            other_start = len(f'{chars},{romans},')
            if length_mismatch:
                warn(0, other_start - 1, 'Word length does not match the number of syllables')

            i = other_start
            for name, value in zip(other_column_names, other_columns):
                if name in other_column_values and value not in other_column_values[name]:
                    error(i, i + len(value), f'Illegal value for column "{name}"')
                i += len(value) + 1

            len_other_column_names = len(other_column_names)
            len_other_columns = len(other_columns)
            if len_other_column_names != len_other_columns:
                warn(i - 1 if len_other_columns > len_other_column_names else other_start, len(line), 'Number of columns does not match the header')

            new_messages += map(lambda line: f'{filename}:{line_num}:{line}', messages)
            cache[filename][line] = messages

        curr_messages[filename] = "\n".join(new_messages)

    print("----- Message Starts -----")
    print(*curr_messages.values(), sep="\n")
    print("----- Message Ends -----")


for filename in iglob("*.csv"):
    lint(filename)

class EventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".csv"):
            lint(basename(event.src_path))

observer = Observer()
observer.schedule(EventHandler(), ".")
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
