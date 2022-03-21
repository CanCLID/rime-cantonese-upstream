from glob import iglob

def sort_criteria(line):
    word, romans, *rest = line.split(',')
    return romans, word, *rest

for filename in iglob('*.csv'):
    with open(filename) as f:
        header = next(f)
        entries = set(f)

    entries_sorted = sorted(entries, key=sort_criteria)

    with open(filename, 'w') as f:
        f.write(header)
        for entry in entries_sorted:
            f.write(entry)
