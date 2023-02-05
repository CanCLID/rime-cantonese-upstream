from glob import iglob
from operator import itemgetter, methodcaller

def compose(f, g):
    return lambda arg: f(g(arg))

sort_cols = {
    'variant.csv': (1, 3, 0, 2)
}

for filename in iglob('*.csv'):
    with open(filename, encoding='utf-8') as f:
        header = next(f).rstrip('\n')
        sort_criteria = methodcaller('split', ',')
        if filename in sort_cols:
            sort_criteria = compose(itemgetter(*sort_cols[filename]), sort_criteria)
        entries = sorted(f, key=sort_criteria)

    with open(filename, 'w', encoding='utf-8') as f:
        print(header, file=f)
        prev_line = None
        for line in entries:
            line = line.rstrip('\n')
            if line != prev_line:
                print(line, file=f)
                prev_line = line
