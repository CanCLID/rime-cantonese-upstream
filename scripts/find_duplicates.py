from collections import defaultdict
from glob import iglob
import sys

line_to_locations = defaultdict(list)

has_error = False
i = 0

for filename in iglob('*.csv'):
    with open(filename, encoding='utf-8') as f:
        next(f)
        for line_num, line in enumerate(f, 2):
            line = line.rstrip('\n')
            location = f'{filename}:{line_num}'
            line_to_locations[line].append(location)

for line, locations in line_to_locations.items():
    if len(locations) > 1:
        locations_str = ', '.join(locations)
        print(f'[{i:04}] \033[91mERROR: "{line}" is duplicated in [{locations_str}]\033[0m', file=sys.stderr)
        has_error = True
        i += 1

if has_error:
    sys.exit(1)
