seen = set()
seen_add = seen.add

for filename in ['fixed_expressions.csv', 'phrase_fragment.csv', 'trending.csv', 'word.csv']:
    with open(filename, encoding='utf-8') as f:
        header = next(f)
        entries = [line for line in f if not (line in seen or seen_add(line))]

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(header)
        f.writelines(entries)
