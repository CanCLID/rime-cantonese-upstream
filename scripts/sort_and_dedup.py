from glob import iglob

def sort_criteria(line):
    word, romans, *_ = line.rstrip('\n').split(',')
    return word, romans, *_

for filename in iglob('*.csv'):
    with open(filename) as f:
        header = next(f)
        entries = set(f)

    entries_sorted = sorted(entries, key=sort_criteria)

    with open(filename, 'w') as f:
        f.write(header)
        f.writelines(entries_sorted)
