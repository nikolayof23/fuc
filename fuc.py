# Copyright 2026, Nikolay Kulikov <nikolayof23@gmail.com>

import re
import subprocess
from collections import defaultdict

# {'d': ['MY_MACRO_1', 'MY_MACRO_2', ..., 'MY_MACRO_N'],
#  'f': ['my_func_1', 'my_func_2', ..., 'my_func_n'],
#  's': ['my_struct_1', 'my_struct_2', ..., 'my_struct_n']}
unused_identifiers = defaultdict(list) # appears once in the code
munused_identifiers = defaultdict(list) # appears twice in the code

# external api:
#   * parse_ctags_file() - read ./tags and fill unused_identifiers and munused_identifiers
#   * get_unused_identifiers() - get list of specified (d, m, f...) unused identifiers
#   * get_munused_identifiers() - get list of specified (d, m, f...) maybe unused identifiers
#
#       Call parse_ctags_file() once first, and only then call get_unused_identifiers()
#       and get_munused_identifiers(), since they use global variables that are populated
#       by parse_ctags_file()

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

# @print_flag: 0 (default) - do not print
#              1 - print only unused identifiers
#              2 - print only maybe unused identifiers
#              3 - print unused and maybe unused identifiers
def parse_ctags_file(print_flag = 0):
    with open("./tags", 'r') as ctags_file:
        for line in ctags_file:
            identifier = get_identifier_name(line)
            if identifier == False:
                continue

            idfr_type = get_identifier_type(line)
            cnt = get_identifier_usage(identifier)
            if cnt > 2:
                continue
            elif cnt == 2:
                munused_identifiers[idfr_type].append(identifier)
                if print_flag == 2:
                    print(f"{idfr_type}:{cnt}:{identifier}")
            elif cnt == 1:
                unused_identifiers[idfr_type].append(identifier)
                if print_flag == 1:
                    print(f"{idfr_type}:{cnt}:{identifier}")

            if print_flag == 3:
                print(f"{idfr_type}:{cnt}:{identifier}")

def get_unused_identifiers(idfr_type: str) -> list:
    return unused_identifiers[idfr_type]

def get_munused_identifiers(idfr_type: str) -> list:
    return munused_identifiers[idfr_type]

#if __name__ == "__main__":
   #parse_ctags_file(3)
