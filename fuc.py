# Copyright 2026, Nikolay Kulikov <nikolayof23@gmail.com>

import re
import subprocess
from collections import defaultdict

# {1: {'d': ['MY_MACRO_1', 'MY_MACRO_2'], 'f': ['my_func_1', 'my_func_2', ]},
#  2: {'d': ['MY_MACRO_9', 'MY_MACRO_n'], 'f': ['my_func_3', 'my_func_4', ]},
#  3: {'d': ['MY_MACRO_b', 'MY_MACRO_a'], 'f': ['my_func_8', 'my_func_9', ]}
#  }
# Keys of the first dict (1, 2, 3...) - the number of times the identifier appears in the code
# Keys of the second dict - see "types of identifiers" below
identifiers = defaultdict(lambda: defaultdict(list))

# external api:
#   * parse_ctags_file() - read ./tags and fill global 'identifiers' dict.
#       It's not printing anything
#   * get_identifiers() - get the list of specified identifiers
#
#       Call parse_ctags_file() once first, and only then call get_identifiers(),
#       since it uses global variables that are populated by parse_ctags_file()

# types of identifiers:
#	'd' - macro
#	'f' - function
#	's' - structure name
#	'u' - unuion name
#	'm' - struct/union member
#	't' - typedef
#	'e' - enumerators (values inside an enum)
#	'g' - enumeration (enum names)
#	'h' - included header
#	'v' - variable


def get_identifier_name(line):
    pattern = r'^!.*'   # comments in the top of ctags file
    if re.match(pattern, line):
        return False

    words_in_line = line.split('\t')
    return words_in_line[0]

# @line - line from ctags file
def get_identifier_type(line: str) -> str:
    sublines = line.split('"')
    right = sublines[1].strip()
    return right.split()[0]

def get_identifier_usage(identifier: str):
    git_grep = subprocess.run(['git', 'grep', '-ch', '-F', f"{identifier}"],
                              capture_output = True,
                              text = True)
    lines = git_grep.stdout.strip()
    str_list = lines.splitlines()
    ret = 0
    for i in str_list:
        if i.isdigit():
            ret += int(i)

    return ret

def parse_ctags_file(use_cnt = 1):
    if use_cnt <= 0:
        return

    with open("./tags", 'r') as ctags_file:
        for line in ctags_file:
            identifier = get_identifier_name(line)
            if identifier == False:
                continue

            idfr_type = get_identifier_type(line)
            cnt = get_identifier_usage(identifier)
            if cnt > use_cnt:
                continue

            identifiers[cnt][idfr_type].append(identifier)

def get_identifiers(identifier_type: str = '?', count: int = 1):
    ret = identifiers[count]

    if len(ret) == 0:
        return []

    if identifier_type == '?':
        tmp = []
        for val in ret.values():
            tmp.extend(val)
        return tmp

    # check "!e", "!dm", "!fgt" ...
    if identifier_type[0] == '!':
        tmp = []

        if len(identifier_type) < 2:
            return tmp

        for key, val in ret.items():
            if key in identifier_type[1:]:
                continue
            tmp.extend(val)
        return tmp

    return ret[identifier_type]

#if __name__ == "__main__":
   #parse_ctags_file()
   #print(get_identifiers("!d"))
