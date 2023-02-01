import jyutping
import time
from glob import iglob
from os.path import basename
from itertools import zip_longest, accumulate
from bisect import bisect
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

non_han = {*'，： '}
other_han = {*'〇﨎﨏﨑﨓﨔﨟﨡﨣﨤﨧﨨﨩'}
multisyllable_allowlist = {*'兡瓸䇉竡尣兛瓩竏𥪕兝瓰竕嗧浬兞瓱竓呎吋啢𠺖兣糎甅竰卅𠯢兙瓧䇆竍卌'}
column_values = {
    "pron_rank": {"預設", "常用", "罕見", "棄用"},
    "tone_var": {"", "本調", "變調"},
    "literary_vernacular": {"", "文讀", "白讀"},
    "class": {"罕見", "日文", "韓文", "來歷不明"},
}

simplified_start = "䌶䜣䞌䢀䥺䦶䭪䯃䲝䴓䶭丬卤纟见觇讠贝车钅长门韦页风飞饣马鱼鸟鹾麦麸黄黾鼋齐齿龙龟鿏鿔鿭鿴𦈈𧮪𧹑𨐅𨰾𨷿𩏼𩖕𩙥𩟾𩧦𩽹𩾁𩾊𩾎𪉁𪎈𪚏𫄙𫌨𫍙𫎦𫐄𫓥𫔬𫖑𫖪𫗇𫗞𫘛𫚈𫛚𫜊𫜑" + \
    "𫜟𫜨𫜲𫟃𫟞𫟤𫟲𫠅𫠊𫠏𫠖𫠜𬌒𬘓𬢇𬣙𬥳𬨁𬬧𬮘𬰱𬱓𬱵𬲥𬳳𬶀𬷕𬷻𬸵𬹅𬹣𬹳𬹺𬺛𮉠𮙉𮝳𮣲𮤫𮧴𮨴𮩛𮪡𮬛𮭡𮭰𮮃𮯙黾𰠗𰫼𰴕𰵊𰷞𰹯𰽕𰿖𰿥𱂃𱂠𱃔𱃱𱄼𱇍𱉇𱊺𱋄𱋾𱌗𱌩𱍁𱭗𱺏𲁑𲂂𲂺𲅀𲇭𲈤𲈵𲊥𲊹𲋎𲋓𲋢𲌄𲍆𲍫𲎑𲎧𲎮"
simplified_end = "䍁䜩䞐䢂䦆䦸䭪䯅䲤䴙䶮丬卤缵觅觑谶赣辚镶长阛韬颧飚飞馕骧鳤鹴鹾麦麺黄黾鼍齑龌龛龟鿏鿕鿭鿺𦈡𧮪𧹗𨐊𨱖𨸎𩐀𩖗𩙰𩠏𩨐𩽿𩾈𩾌𩾎𪉕𪎐𪚐𫄹𫌭𫍿𫎬𫐙𫔕𫔹𫖖𫖺𫗌𫗵𫘱𫚭𫜆𫜊𫜕" + \
    "𫜟𫜰𫜳𫟇𫟢𫟦𫠂𫠈𫠌𫠒𫠗𫠜𬌒𬙋𬢔𬤱𬦀𬨕𬮃𬮹𬰸𬱳𬲈𬳔𬴐𬶻𬷕𬸱𬸹𬹎𬹤𬹳𬺖𬺞𮉯𮙋𮝺𮣷𮤸𮧵𮨶𮩞𮪥𮬤𮭪𮭰𮮇𮯙黾𰠘𰭁𰴞𰶏𰷮𰺤𰿊𰿖𱀀𱂌𱂻𱃠𱄊𱅬𱈜𱊵𱊽𱋮𱌉𱌙𱌽𱍈𱭘𱺰𲁙𲂗𲃆𲅃𲈡𲈥𲉈𲊥𲋃𲋑𲋓𲋬𲌋𲍙𲎊𲎓𲎫𲎮"

ignoreroman_list = {}

cache = {}
headers = {}
curr_messages = {}

def is_unified_ideograph(char):
    return '\u4e00' <= char <= '\u9fff' or \
           '\u3400' <= char <= '\u4dbf' or \
           '\U00020000' <= char <= '\U0002a6df' or \
           '\U0002a700' <= char <= '\U0002ebef' or \
           '\U00030000' <= char <= '\U000323af' or \
           char in other_han

def is_simplified_ideograph(char):
    return "䌶" <= char <= simplified_end[bisect(simplified_start, char) - 1]

def get_additional_information(char):
    return ': Radicals' if '\u2e80' <= char <= '\u2fef' else \
           ': Symbols and Punctuation' if '\u3000' <= char <= '\u303f' else \
           ': Strokes' if '\u31c0' <= char <= '\u31ef' else \
           ': Compatibility Ideographs' if '\uf900' <= char <= '\ufaff' else \
           ': Compatibility Ideographs Supplement' if '\U0002f800' <= char <= '\U0002fa1f' else \
           ''

def is_ascii_lowercase_letter(char):
    return 'a' <= char <= 'z'

def is_ascii_letter(char):
    return 'A' <= char <= 'Z' or 'a' <= char <= 'z'

def utf16_byte_length(char):
    return (char >= '\U00010000') + 1

def column_start(column):
    return len(column) + 1

def lint(filename):
    with open(filename, encoding='utf-8') as f:
        new_messages = []

        first_line = next(f, "")
        column_names = first_line.rstrip('\n').split(',')
        chars_column_index = column_names.index("char") if "char" in column_names else None
        romans_column_index = column_names.index("jyutping") if "jyutping" in column_names else None
        start_column_index = min(chars_column_index or 0, romans_column_index or 0)
        end_column_index = max(chars_column_index or 0, romans_column_index or 0)

        if first_line != headers.get(filename):
            cache[filename] = {}

        for line_num, line in enumerate(f, 2):
            if line in cache[filename]:
                new_messages += [f'{filename}:{line_num}:{line}' for line in cache[filename][line]]
                continue
            messages = []

            def error(start, end, message):
                messages.append(f'{utf16_column_mapper[start]},{utf16_column_mapper[end]}: ERROR: {message}')

            def warn(start, end, message):
                messages.append(f'{utf16_column_mapper[start]},{utf16_column_mapper[end]}: WARNING: {message}')

            def yield_chars(chars, start):
                s = ''
                is_punctuation = True
                is_leading = True
                for i, char in enumerate(chars, start):
                    if (char in non_han) != is_punctuation:
                        if s:
                            if is_punctuation:
                                if is_leading:
                                    error(i - len(s), i, "Leading punctuation or space is not allowed")
                                elif len(s) > 1:
                                    error(i - len(s), i, "Continuous punctuation or spaces are not allowed")
                            else:
                                yield (i, s)
                            s = ''
                        is_punctuation = not is_punctuation
                        is_leading = False
                    if not is_punctuation and s and not (is_ascii_lowercase_letter(char) and is_ascii_letter(s[-1])):
                        yield (i, s)
                        s = ''
                    s += char
                if s:
                    i += 1
                    if is_punctuation:
                        error(i - len(s), i, "Trailing punctuation or space is not allowed")
                    else:
                        yield (i, s)

            def yield_romans(romans, start):
                s = ''
                is_space = True
                is_leading = True
                for i, roman in enumerate(romans, start):
                    if (roman == ' ') != is_space:
                        if s:
                            if is_space:
                                if is_leading:
                                    error(i - len(s), i, "Leading space is not allowed")
                                elif len(s) > 1:
                                    error(i - len(s), i, "Continuous spaces are not allowed")
                            else:
                                yield (i, s)
                            s = ''
                        is_space = not is_space
                        is_leading = False
                    s += roman
                if s:
                    i += 1
                    if is_space:
                        error(i - len(s), i, "Trailing space is not allowed")
                    else:
                        yield (i, s)

            utf16_column_mapper = list(accumulate(map(utf16_byte_length, line), initial=1))
            columns = line.rstrip('\n').split(',')
            columns_start = list(accumulate(map(column_start, columns), initial=0))
            columns_end = list(accumulate(map(column_start, columns[1:]), initial=len(columns[0])))

            if chars_column_index is not None and romans_column_index is not None:
                if chars_column_index < len(columns) > romans_column_index:
                    length_mismatch = False
                    for (char_i, char), (roman_i, roman) in zip_longest(
                        yield_chars(columns[chars_column_index], columns_start[chars_column_index]),
                        yield_romans(columns[romans_column_index], columns_start[romans_column_index]),
                        fillvalue=(None, None)
                    ):
                        if length_mismatch is not None and (not char or not roman):
                            length_mismatch = True
                        if char:
                            if char in multisyllable_allowlist:
                                length_mismatch = None
                            if not is_ascii_letter(char):
                                if is_simplified_ideograph(char):
                                    warn(char_i - len(char), char_i, f'Character "{char}" is definitely a simplified ideograph')
                                elif not is_unified_ideograph(char):
                                    error(char_i - len(char), char_i, f'Invalid character "{char}"{get_additional_information(char)}')
                        if roman and (char, roman) not in ignoreroman_list:
                            status = jyutping.validate(roman)
                            if status == jyutping.ValidationStatus.UNCOMMON:
                                warn(roman_i - len(roman), roman_i, f'Uncommon jyutping: "{roman}"')
                            elif status == jyutping.ValidationStatus.INVALID:
                                error(roman_i - len(roman), roman_i, f'Invalid jyutping: "{roman}"')

                    if length_mismatch:
                        warn(columns_start[start_column_index], columns_end[end_column_index], 'Word length does not match the number of syllables')
                else:
                    error(0, columns_end[-1], "Invalid line")
            else:
                if chars_column_index is not None:
                    if chars_column_index < len(columns):
                        for char_i, char in yield_chars(columns[chars_column_index], columns_start[chars_column_index]):
                            if not is_ascii_letter(char):
                                if is_simplified_ideograph(char):
                                    warn(char_i - len(char), char_i, f'Character "{char}" is definitely a simplified ideograph')
                                elif not is_unified_ideograph(char):
                                    error(char_i - len(char), char_i, f'Invalid character "{char}"{get_additional_information(char)}')
                    else:
                        error(0, columns_end[-1], "Invalid line")
                if romans_column_index is not None:
                    if romans_column_index < len(columns):
                        for roman_i, roman in yield_romans(columns[romans_column_index], columns_start[romans_column_index]):
                            status = jyutping.validate(roman)
                            if status == jyutping.ValidationStatus.UNCOMMON:
                                warn(roman_i - len(roman), roman_i, f'Uncommon jyutping: "{roman}"')
                            elif status == jyutping.ValidationStatus.INVALID:
                                error(roman_i - len(roman), roman_i, f'Invalid jyutping: "{roman}"')
                    else:
                        error(0, columns_end[-1], "Invalid line")

            for i, (name, value) in enumerate(zip(column_names, columns)):
                if name in column_values and value not in column_values[name]:
                    error(columns_start[i], columns_end[i], f'Illegal value for column "{name}"')

            len_column_names = len(column_names)
            len_columns = len(columns)
            if len_column_names != len_columns:
                warn(columns_end[i], columns_end[-1], 'Number of columns does not match the header')

            new_messages += [f'{filename}:{line_num}:{line}' for line in messages]
            cache[filename][line] = messages

        curr_messages[filename] = "\n".join(new_messages)

    print("----- Message Starts -----")
    print(*curr_messages.values(), sep="\n")
    print("----- Message Ends -----")

def start_linter():
    global ignoreroman_list, cache, headers, curr_messages
    with open('scripts/ignore.csv', encoding='utf-8') as f:
        next(f, "")
        ignoreroman_list = set(map(lambda line: tuple(line.rstrip('\n').split(',')), f))
    cache = {}
    headers = {}
    curr_messages = {}
    for filename in iglob("*.csv"):
        lint(filename)

class EventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".csv"):
            time.sleep(0.01)
            lint(basename(event.src_path))

class RestartHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".csv"):
            time.sleep(0.01)
            start_linter()

start_linter()

observer = Observer()
observer.schedule(EventHandler(), ".")
observer.schedule(RestartHandler(), "./scripts")
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
