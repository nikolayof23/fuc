# The Find Unused Code script

## Overview

This script reads the `tags` file (which can be generated using `ctags -R .`)
and uses it to search for unused identifiers (functions, macros, etc.) via
`git grep` (note that the `git grep` command is executed for *every* identifier
in the tags file).

It provides the following functions:

* `parse_ctags_file(use_cnt: int)` - Read the `./tags` file and load the found
info into global dictionaries. Call this function before the very first one; the
others are meaningless without it.
    - `@use_cnt` - all identifiers appearing more frequently than `use_cnt` are
    not loaded. Default `1`

* `get_identifiers(identifier_type: str, count: int)` - get an array of string
containing identifiers.
    - `@identifier_type` -  identifier type, single letter string - 'f', 'd';
    Default '?' - combine all identifiers;
    '!dfs' - include evrything, except 'd', 'f', 's'.
    - `@count` - return identifiers that appear exactly `count` times.
    Default `1`.

* `print_identifiers(cnt: int)` - display the total number of identifiers in group.
    - `cnt` - print identifiers that appear exactly `count` times.
    Default `1`, "unused".


### Types of identifiers (from ctags):
    - 'd' - macro
    - 'f' - function
    - 's' - structure name
    - 'u' - unuion name
    - 'm' - struct/union member
    - 't' - typedef
    - 'e' - enumerators (values inside an enum)
    - 'g' - enumeration (enum names)
    - 'h' - included header
    - 'v' - variable



## Integration with Vim

I originally planned to use it from Vim, so here is a part of my ~/.vimrc file:

```vim
py3file ~/scripts/uc/fuc.py

let g:fuc_info = []
let g:fuc_index = 0
function FucParse()
    :py3 parse_ctags_file()
    echo "Success"
endfunction
":call FucLoad('d') - load unused macros
function FucLoad(identifier_type)
    let cmd = printf('get_identifiers("%s", %s)', a:identifier_type, a:use_count)

    let g:fuc_info = py3eval(cmd)
    let g:fuc_index = 0
    echo len(g:fuc_info) . " identifiers found"
endfunction

function FucJumpToNext()
    execute "tag " . g:fuc_info[g:fuc_index]
    let g:fuc_index += 1
endfunction

function FucShowUnused()
	echo py3eval("print_identifiers()")
endfunction


nnoremap <F6> :call FucJumpToNext() <CR>
```

Thus, usage boils down to opening the required file, calling FucParse() and
FucLoad(), and then simply pressing F6:

    $ vim hal/hal_com.c
    (vim) :call FucParse()
        ... wait a few seconds ...
    (vim) :call FucLoad('d')
    (vim) <F6>, <F6>...
    (vim) <C-t>, <C-t>...
    (vim) :tabnew ...


## Execution from the terminal
Run the script with the `--check_code` flag to check the C source code in the
current directory and output brief statistics using `print_identifiers()`:

`python ./path/to/fuc.py --check-code ./`


Running the script without parameters has no effect;
it is intended for correct loading from ~/.vimrc
