import re


def convertCamel(name):
    return re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
