"""
Finds all duplicated lines within each CSV file as well as across all files.
It outputs a duplicates.tsv containing the duplicated lines and
a list of two or more filenames with the line number of the duplicated lines.

Sample line in duplicates.tsv looks like:
到未啊,dou3 mei6 aa3	[phrase_fragment.csv:1830, word.csv:11234]

This means that the line "到未啊,dou3 mei6 aa3" is duplicated
in phrase_fragment.csv on line 1830 and in word.csv on line 11234.
"""
from glob import iglob

line_to_locations = {}

for filename in iglob('*.csv'):
    with open(filename) as f:
        assert next(f).startswith('char,jyutping'), 'Invalid CSV header'
        
        for line_num, line in enumerate(f, 2):
            location = f'{filename}:{line_num}'
            if line in line_to_locations:
                line_to_locations[line].append(location)
            else:
                line_to_locations[line] = [location]

f = open('duplicates.tsv', 'w')

for line, locations in line_to_locations.items():
    if len(locations) > 1:
        locations_str = ', '.join(locations)
        f.write(f'{line.strip()}\t[{locations_str}]\n')

f.close()
