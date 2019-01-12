
## ncm2-d

neovim/vim [ncm2](https://github.com/ncm2/ncm2) autocompletion source for [D](https://www.dlang.org).

![screenshot](https://s2.gifyu.com/images/ncm2-d_cropped.gif)

## Install D

This plugin relies on D tools like `dcd-server`, `dcd-client` and `dub` to provide autocompletion. Make sure you have them available in your PATH.

## Plugin Install

- You have to install both `ncm2` and `ncm2-d`.
- `nvim-yarp` is only needed to provide compatibility with vim 8.

If you're using dein:

```
call dein#add('ncm2/ncm2')
call dein#add('ncm2/ncm2-d', {'on_ft': 'd'})
call dein#add('roxma/nvim-yarp')

" enable ncm2 for all buffers and set completeopt
autocmd BufEnter * call ncm2#enable_for_buffer()
set completeopt=noinsert,menuone
```

If you're using vim-plug:

```
Plug 'ncm2/ncm2'
Plug 'ncm2/ncm2-d', { 'for': 'd' }
Plug 'roxma/nvim-yarp'

" enable ncm2 for all buffers and set completeopt
autocmd BufEnter * call ncm2#enable_for_buffer()
set completeopt=noinsert,menuone
```

## Settings

This plugin just works without any extra settings (packages installed with dub are already included path when starting `dcd-server`). If needed, you can adjust these variables:

```
let g:ncm2_d#dcd_client_bin = 'dcd-client'
let g:ncm2_d#dcd_client_args = ['']
let g:ncm2_d#dcd_server_bin = 'dcd-server'
let g:ncm2_d#dcd_server_args = ['-I/usr/include/dlang/dmd']
let g:ncm2_d#dcd_autostart_server = 1
```
