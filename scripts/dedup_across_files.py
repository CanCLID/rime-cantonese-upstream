from glob import iglob

seen = set()
seen_add = seen.add

for filename in iglob('*.csv'):
    with open(filename, encoding='utf-8') as f:
        header = next(f).rstrip('\n')
        if header != 'char,jyutping':
            continue
        entries = []
        entries_append = entries.append
        for line in f:
            line = line.rstrip('\n')
            if line not in seen:
                entries_append(line)
                seen_add(line)

    with open(filename, 'w', encoding='utf-8') as f:
        print(header, file=f)
        for line in entries:
            print(line, file=f)
