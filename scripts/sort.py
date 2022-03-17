from glob import iglob

def sort_criteria(line):
    word, romans, *rest = line.split(',')
    return romans, word, *rest

for filename in iglob('*.csv'):
    with open(filename) as f:
        header = next(f)
        entries = list(f)

    entries.sort(key=sort_criteria)

    with open(filename, 'w') as f:
        f.write(header)
        for entry in entries:
            f.write(entry)
