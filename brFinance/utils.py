def extract_substring(start, end, string):
    return string.split(start)[-1].split(end)[0]
