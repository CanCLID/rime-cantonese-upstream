from glob import iglob

def sort_criteria(line):
    return tuple(line.split(','))

def variant_sort_criteria(line):
    columns = line.split(',')
    return (columns[1], columns[3], columns[0], columns[2])

for filename in iglob('*.csv'):
    with open(filename, encoding='utf-8') as f:
        header = next(f).rstrip('\n')
        seen = set()
        seen_add = seen.add
        entries = []
        entries_append = entries.append
        for line in f:
            line = line.rstrip('\n')
            if line not in seen:
                entries_append(line)
                seen_add(line)

    if filename == 'variant.csv':
        entries_sorted = sorted(entries, key=variant_sort_criteria)
    else:
        entries_sorted = sorted(entries, key=sort_criteria)

    with open(filename, 'w', encoding='utf-8') as f:
        print(header, file=f)
        for line in entries_sorted:
            print(line, file=f)
