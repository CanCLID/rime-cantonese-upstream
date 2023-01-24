import re

class Validator:
    def __init__(self, groups):
        self.groups = groups

    def test(self, test_set):
        return max(self.test_rule(rule_set) for rule_set in test_set.values())

    def test_rule(self, rule_set):
        for level, matchers in rule_set:
            if all(Validator.match(matcher, group) for matcher, group in zip(matchers, self.groups)):
                return level
        return ValidationStatus.VALID

    @staticmethod
    def match(matcher, group):
        return matcher is None or group in ['' if part == '-' else part for part in matcher.split(' ')]

class ValidationStatus:
    VALID = 0
    UNCOMMON = 1
    INVALID = 2

def validate(jyutping):
    '''
    >>> validate('jyut6')
    0  # ValidationStatus.VALID
    >>> validate('fing6')
    1  # ValidationStatus.UNCOMMON
    >>> validate('nguk1')
    2  # ValidationStatus.INVALID
    '''
    match = re.match('^([gk]w?|ng|[bpmfdtnlhwzcsj]?)(?![1-6]$)(aa?|oe?|eo?|y?u|i?)(ng|[iumnptk]?)([1-6])$', jyutping)
    if match is None: return ValidationStatus.INVALID
    return validate_args(*match.groups())

def validate_args(*args):
    '''
    >>> validate('j', 'yu', 't', '6')
    0  # ValidationStatus.VALID
    >>> validate('gw', 'e', 'k', '6')
    1  # ValidationStatus.UNCOMMON
    >>> validate('ng', 'u', 'k', '1')
    2  # ValidationStatus.INVALID
    '''
    valid, alert, error = ValidationStatus.VALID, ValidationStatus.UNCOMMON, ValidationStatus.INVALID
    return Validator(args).test({
        'Onset - Nucleus - Coda': [
            (valid, ('-', '-', 'm ng')),
            (alert, ('h', '-', 'm ng')),
            (error, (None, '-', None)),

            (error, ('b p m f gw kw w', 'o', 'i')),
            (valid, ('z c s j', 'yu', '-')),
            (error, (None, 'yu', '-')),

            (error, ('-', 'aa', 'm')),
            (error, ('p h', 'aa', 't')),

            (valid, ('n', 'aa', 'u')),
            (alert, ('d', 'aa', 'k')),
            (error, ('f d t n', 'aa', 'u ng k')),
            (error, ('k', 'aa', 'm n ng p t k')),

            (alert, ('n', 'a', 't k')),
            (error, ('t', 'a', 't k')),
            (error, ('p f', 'a', 'k')),
            (alert, ('ng k', 'a', 'ng')),
            (alert, ('-', 'a', 'n t')),
            (alert, ('g k w', 'a', 'k')),

            (alert, ('k', 'o', '-')),
            (error, ('f', 'o', 'u')),

            (error, ('t', 'e', '-')),
            (error, ('t z c j', 'e', 'i')),
            (error, ('f n', 'e', 'ng')),
            (error, ('b m f n g j', 'e', 'k')),

            (alert, ('t k l z s', 'oe', '-')),
            (error, ('n c j', 'oe', '-')),
            (error, ('t', 'oe', 'ng')),
            (error, ('t h', 'oe', 'k')),

            (error, ('n', 'eo', 'n')),
            (error, ('j', 'eo', 't')),
            (error, ('g k h', 'eo', 'n t')),

            (error, ('p f t k', 'i', '-')),
            (error, ('f', 'i', 'n')),
            (error, ('w', 'i', '- n t')),

            (error, ('b p m', 'u', '-')),
            (error, ('k', 'u', 'n')),
            (error, ('w', 'u', 'ng k')),

            (error, ('n', 'yu', 't')),

            (alert, ('kw', 'aa', 'i')),
            (error, ('kw', 'aa', 'n')),
            (error, ('kw', 'a', 'k')),
            (error, ('kw', 'o', '-')),
            (error, ('kw', 'i', 'ng')),

            (error, ('j', 'aa', 'm n t')),
            (error, ('j', 'a', 'ng k')),
        ],
        'Nucleus - Coda': [
            (valid, ('- m l g z', 'a', '-')),
            (error, (None, 'a', '-')),

            (valid, ('- g ng h', 'o', 'n')),
            (valid, ('g h', 'o', 't')),
            (alert, ('l z', 'e', 'u')),
            (alert, ('b p d ng', 'e', 't')),
            (error, (None, 'o e', 'm n p t')),

            (valid, (None, 'oe', '- ng k')),
            (alert, ('z c', 'oe', 't')),
            (error, (None, 'oe', None)),
            (valid, (None, 'eo', 'i n t')),
            (error, (None, 'eo', None)),

            (error, (None, 'i', 'i')),
            (error, (None, 'u', 'u m p')),
            (valid, (None, 'yu', '- n t')),
            (error, (None, 'yu', None)),
        ],
        'Onset - Coda': [
            (error, ('gw kw w', None, 'u')),
            (error, ('b p m f gw kw w', None, 'm p')),
            (error, ('kw', None, 't')),
        ],
        'Onset - Nucleus': [
            (error, ('- b p m f ng gw kw w', 'oe eo yu', None)),

            (alert, ('f', 'i', None)),
            (error, ('j', 'o', None)),

            (valid, ('-', 'e', '-')),
            (alert, ('-', 'e', 'i')),
            (error, ('-', 'e', None)),

            (valid, ('-', 'u', 'ng k')),
            (alert, ('-', 'i', 'k')),
            (error, ('-', 'i u', None)),

            (alert, ('ng', 'i e', 't')),
            (alert, ('- ng gw w', 'e', '-')),
            (error, ('ng gw kw w', 'e', None)),
            (valid, ('gw kw', 'i', 'ng k')),
            (error, ('ng gw kw', 'i u', None)),

            (valid, ('d t n l h z c s j', 'u', 'ng k')),
            (error, ('d t n l h z c s j', 'u', None)),
        ],
        'Other': [
            (alert, (None, None, 'p t k', '4 5')),
        ],
    })
