from glob import iglob

def sort_criteria(line):
    return tuple(line.rstrip('\n').split(','))

for filename in iglob('*.csv'):
    with open(filename, encoding='utf-8') as f:
        header = next(f)
        entries = set(f)

    entries_sorted = sorted(entries, key=sort_criteria)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(header)
        f.writelines(entries_sorted)
