if get(s:, 'ncm2_d', 0)
  finish
endif
let s:ncm2_d = 1

let g:ncm2_d#dcd_client_bin = get(g:, 'ncm2_d#dcd_client_bin', 'dcd-client')
let g:ncm2_d#dcd_client_args = get(g:, 'ncm2_d#dcd_client_args', [''])
let g:ncm2_d#dcd_server_bin = get(g:, 'ncm2_d#dcd_server_bin', 'dcd-server')
let g:ncm2_d#dcd_server_args_str = get(g:, 'ncm2_d#dcd_server_args', '-I/usr/include/dmd/druntime/import -I/usr/include/dmd/phobos -I/usr/include/dlang/dmd')
let g:ncm2_d#dcd_server_args = get(g:, 'ncm2_d#dcd_server_args', ['-I/usr/include/dmd/druntime/import', '-I/usr/include/dmd/phobos', '-I/usr/include/dlang/dmd'])
let g:ncm2_d#dcd_autostart_server = get(g:, 'ncm2#dcd_autostart_server', 1)

let g:ncm2_d#proc = yarp#py3('ncm2_d')

if g:ncm2_d#dcd_autostart_server == 1
  let g:ncm2_d_dcd#proc = yarp#py3('ncm2_d_dcd')
endif

let g:ncm2_d#source = extend(
      \ get(g:, 'ncm2_d#source', {}), {
      \ 'name': 'd',
      \ 'priority': 9,
      \ 'mark': 'd',
      \ 'early_cache': 1,
      \ 'subscope_enable': 1,
      \ 'scope': ['d'],
      \ 'word_pattern': '\w+',
      \ 'complete_pattern': ['\.'],
      \ 'complete_length': 1,
      \ 'on_complete': 'ncm2_d#on_complete',
      \ 'on_warmup': 'ncm2_d#on_warmup',
      \ }, 'keep')

function! s:DCDdirs()
  if executable("dub")
    let res = system("dub list")
    let uniqPackages = {}
    for line in split(res, "\n")
      let elements = split(line, " ")
      if len(elements) == 3 " pkg, version and dir..
        let [package, pversion, dir] = elements
        if has_key(uniqPackages, package)
          let value = uniqPackages[package][1]
          if value < pversion
            let uniqPackages[package] = [dir, pversion]
          endif
        else
          let uniqPackages[package] = [dir, pversion]
        endif
      endif
    endfor
    let srcDirs = ["source", "src"]
    let uniqDirs = []
    for dir in values(uniqPackages)
      for srcDir in srcDirs
        let folder = dir[0] . srcDir
        if isdirectory(folder)
          call add(uniqDirs, folder)
        endif
      endfor
    endfor
    return uniqDirs
  else
    echoerr("binary 'dub' not found. please, install dub first.")
  endif
endfunction

function! s:DCDDirsInc()
  let ddirs = s:DCDdirs()
  let args = []
  for f in ddirs
    call add(args, "-I" . f)
  endfor
  return args
endfunction

let g:ncm2_d#dcd_inc_dirs = s:DCDDirsInc()

func! ncm2_d#init()
  let g:ncm2_d#dcd_inc_dirs = s:DCDDirsInc()
  call ncm2#register_source(g:ncm2_d#source)
endfunc

func! ncm2_d#on_warmup(ctx)
  call g:ncm2_d#proc.jobstart()
  call g:ncm2_d_dcd#proc.jobstart()
endfunc

func! ncm2_d#on_complete(ctx)
  call g:ncm2_d#proc.try_notify('on_complete',
        \ a:ctx,
        \ ncm2_d#data(),
        \ getline(1, '$'))
endfunc

func! ncm2_d#error(msg)
  call g:ncm2_d#proc.error(a:msg)
endfunc

func! ncm2_d#data()
  return {
        \ 'dcd_client_bin': g:ncm2_d#dcd_client_bin,
        \ 'dcd_client_args': g:ncm2_d#dcd_client_args,
        \ 'dcd_server_bin': g:ncm2_d#dcd_server_bin,
        \ 'dcd_server_args': g:ncm2_d#dcd_server_args,
        \ 'dcd_inc_dirs': g:ncm2_d#dcd_inc_dirs,
        \ }
endfunc
