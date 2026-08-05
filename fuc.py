# Copyright 2026, Nikolay Kulikov <nikolayof23@gmail.com>

import subprocess
import json
from collections import defaultdict

# {1: {'d': ['MY_MACRO_1', 'MY_MACRO_2'], 'f': ['my_func_1', 'my_func_2', ]},
#  2: {'d': ['MY_MACRO_9', 'MY_MACRO_n'], 'f': ['my_func_3', 'my_func_4', ]},
#  3: {'d': ['MY_MACRO_b', 'MY_MACRO_a'], 'f': ['my_func_8', 'my_func_9', ]}
#  }
# Keys of the first dict (1, 2, 3...) - the number of times the identifier appears in the code
# Keys of the second dict - see "types of identifiers" below
identifiers = defaultdict(lambda: defaultdict(list))


def print_identifiers(cnt: int = 1):
    print(f"{len(identifiers[cnt]['d'])} unused macros")
    print(f"{len(identifiers[cnt]['f'])} unused functions")
    print(f"{len(identifiers[cnt]['s'])} unused structures")
    print(f"{len(identifiers[cnt]['u'])} unused unions")
    print(f"{len(identifiers[cnt]['m'])} unused members")
    print(f"{len(identifiers[cnt]['t'])} unused typedefs")
    print(f"{len(identifiers[cnt]['e'])} unused enumerators")
    print(f"{len(identifiers[cnt]['g'])} unused enumerations")
    print(f"{len(identifiers[cnt]['h'])} unused headers")
    print(f"{len(identifiers[cnt]['v'])} unused variables")

# external api:
#   * parse_ctags_file() - read ./tags and fill global 'identifiers' dict.
#       It's not printing anything
#   * get_identifiers() - get the list of specified identifiers
#   * print_identifiers() - display the total number of identifiers in the group @cnt
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

def is_c_src_file(filename: str) -> bool:
    if len(filename) < 2:
        return False

    return filename[-2] == '.' and (filename[-1] == 'c' or filename[-1] == 'h')

# converts ctags file line to list:
# ['IDENTIFIER_NAME', './path/to/file', 'identifier_type']
def parse_c_ctags_line(line: str) -> list[str]:
    ret = []
    words = line.split('\t')
    ret.append(words[0]) # get identifier name and filename because they don't contain a tabs
    ret.append(words[1])

    # split the line by 2
    #   left - isn't need, we already have idfr name and filename; the vim command isn't need
    #   right - identifier type, and something other, use
    right = line.split('"')[1]
    right = right.strip()
    right = right.split('\t') # next everything is split by tabs
    ret.append(right[0])
    return ret

def parse_ctags_file(use_cnt = 1):
    if use_cnt <= 0:
        return

    with open("./tags", 'r') as ctags_file:
        for line in ctags_file:
            if line[0] == '!':
                continue

            line = line.strip()

            words_in_line = parse_c_ctags_line(line)
            if not is_c_src_file(words_in_line[1]):
                continue
            identifier = words_in_line[0]
            idfr_type = words_in_line[2]
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

def load_dict_to_file(filename: str, data: dict):
    with open(filename, 'a') as file:
        json.dump(data, file, indent = 4)

#if __name__ == "__main__":
   #parse_ctags_file()
   #load_dict_to_file("./fuc-data.json", identifiers)
   #print(get_identifiers("!d"))
