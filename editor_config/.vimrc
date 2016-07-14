set nocompatible

set history=1024

filetype on 


set iskeyword+=_,$,@,%,#,-

syntax on
syntax enable

set nu

set lbr

set autoread

set cursorline

autocmd VimEnter * call BufPos_Initialize()

set ffs=unix,dos,mac "Default file types

vnoremap <silent> gv :call VisualSearch('gv')<CR>

try
    call fuf#defineLaunchCommand('FufCWD', 'file', 'fnamemodify(getcwd(), ''%:p:h'')')
    map <leader>t :FufCWD **/<CR>
catch
endtry

noremap <Leader>m mmHmt:%s/<C-V><cr>//ge<cr>'tzt'm

map <leader>q :e ~/buffer<cr>

if has("win32")
    let $VIMFILES = $VIM.'/vimfiles'
else
    let $VIMFILES = $HOME.'/.vim'
endif

if has("gui_running")
set cursorline
  hi cursorline guibg=#8DC36D
  set cursorcolumn
  hi CursorColumn guibg=#8DC36D
endif

map <leader>cd :cd %:p:h<cr>


set nobackup

setlocal noswapfile
set bufhidden=hide

set wildmenu

set ruler
set rulerformat=%20(%2*%<%f%=\ %m%r\ %3l\ %c\ %p%%%)

set cmdheight=1

set backspace=2
set backspace=eol,start,indent

set whichwrap+=<,>,h,l

"set shortmess=atI

set report=0

set noerrorbells


set showmatch

set matchtime=5


set incsearch

set listchars=tab:\|\ ,trail:.,extends:>,precedes:<,eol:$

set scrolloff=3

set novisualbell


set laststatus=2

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" => VIM userinterface
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"Set 7 lines to the curors - when moving vertical..
set so=7

"Do not redraw, when running macros.. lazyredraw
set lz

"Change buffer - without saving
set hid

"Set magic on
set magic

"How many tenths of a second to blink
set mat=2

"set formatoptions=tcrqn


set softtabstop=4
set shiftwidth=4

set noexpandtab

"set nowrap


"set textwidth=120

set foldenable              
set foldmethod=syntax      
set foldcolumn=0          
setlocal foldlevel=1     
set foldlevel=100       
set foldclose=all      

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

set guioptions-=T
set guioptions-=m
map <silent> <F2> :if &guioptions =~# 'T' <Bar>
\set guioptions-=T <Bar>
\set guioptions-=m <bar>
\else <Bar>
\set guioptions+=T <Bar>
\set guioptions+=m <Bar>
\endif<CR>

au GUIEnter * simalt ~x "maximum the initial window


vnoremap $1 <esc>`>a)<esc>`<i(<esc>
vnoremap $2 <esc>`>a]<esc>`<i[<esc>
vnoremap $3 <esc>`>a}<esc>`<i{<esc>
vnoremap $$ <esc>`>a"<esc>`<i"<esc>
vnoremap $q <esc>`>a'<esc>`<i'<esc>
vnoremap $e <esc>`>a"<esc>`<i"<esc>

inoremap $1 ()<esc>i
inoremap $2 []<esc>i
inoremap $3 {}<esc>i
inoremap $4 {<esc>o}<esc>O
inoremap $q ''<esc>i
inoremap $e ""<esc>i

vnoremap $w <esc>`>a"<esc>`<i"<esc>
"vnoremap $w <esc>`>a><esc>`<i<<esc>
"vnoremap $w <esc>'>a”<esc>`<i“<esc>

set foldenable
set foldmethod=manual
nnoremap <space> @=((foldclosed(line('.')) < 0) ? 'zc' : 'zo')<CR>

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" => Command mode related
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Smart mappings on the command line
cno $h e ~/
cno $d e ~/Desktop/
cno $j e ./
cno $c e <C-\>eCurrentFileDir("e")<cr>

" $q is super useful when browsing on the command line
cno $q <C-\>eDeleteTillSlash()<cr>

cnoremap <C-A>      <Home>
cnoremap <C-E>      <End>
cnoremap <C-K>      <C-U>



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" => Moving around, tabs and buffers
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Map space to / (search) and c-space to ? (backgwards search)
"map <space> /
"map <c-space> ?
"map <silent> <leader><cr> :noh<cr>

map <C-j> <C-W>j
map <C-k> <C-W>k
map <C-h> <C-W>h
map <C-l> <C-W>l

map <leader>bd :Bclose<cr>

map <leader>ba :1,300 bd!<cr>

map <leader>tn :tabnew %<cr> " 译注:将当前内容在新标签中打开
map <leader>te :tabedit      " 译注:打开空白新标签
map <leader>tc :tabclose<cr> " 译注:关闭当前标签
map <leader>tm :tabmove      " 译注:移动当前标签,使用方法为

" When pressing <leader>cd switch to the directory of the open buffer
map <leader>cd :cd %:p:h<cr>

" Specify the behavior when switching between buffers
"try
  "set switchbuf=usetab
  "set stal=2
"catch
"endtry


nnoremap <TAB> :MBEbn<CR>
nnoremap <C-TAB> :MBEbp<CR>


let NERDSpaceDelims=1       
let NERDCompactSexyComs=1  

let g:winManagerWindowLayout = 'FileExplorer'
let g:winManagerWidth = 30
let g:defaultExplorer = 0
map <C-W><C-F> :FirstExplorerWindow<cr>
map <C-W><C-B> :BottomExplorerWindow<cr>
map <C-W><C-T> :WMToggle<cr>

 


" if file not opened, create a new tab, or switch to the opened file
function! SwitchToBuf(filename)
 " find in current tab
 let bufwinnr = bufwinnr(a:filename)
 if bufwinnr != -1
 exec bufwinnr . "wincmd w"
 return
 else
 " search each tab
 tabfirst
 let tb = 1
 while tb <= tabpagenr("$")
 let bufwinnr = bufwinnr(a:filename)
 if bufwinnr != -1
 exec "normal " . tb . "gt"
 exec bufwinnr . "wincmd w"
 return
 endif
 tabnext
 let tb = tb +1
 endwhile
 " not exist, new tab
 exec "tabnew " . a:filename
 endif
endfunction


function! MyDiff()
  let opt = '-a --binary '
  if &diffopt =~ 'icase' | let opt = opt . '-i ' | endif
  if &diffopt =~ 'iwhite' | let opt = opt . '-b ' | endif
  let arg1 = v:fname_in
  if arg1 =~ ' ' | let arg1 = '"' . arg1 . '"' | endif
  let arg2 = v:fname_new
  if arg2 =~ ' ' | let arg2 = '"' . arg2 . '"' | endif
  let arg3 = v:fname_out
  if arg3 =~ ' ' | let arg3 = '"' . arg3 . '"' | endif
  let eq = ''
  if $VIMRUNTIME =~ ' '
    if &sh =~ '\<cmd'
      let cmd = '""' . $VIMRUNTIME . '\diff"'
      let eq = '"'
    else
      let cmd = substitute($VIMRUNTIME, ' ', '" ', '') . '\diff"'
    endif
  else
    let cmd = $VIMRUNTIME . '\diff'
  endif
  silent execute '!' . cmd . ' ' . opt . arg1 . ' ' . arg2 . ' > ' . arg3 . eq
endfunction


function! BufPos_ActivateBuffer(num)
 let l:count = 1
 for i in range(1, bufnr("$"))
 if buflisted(i) && getbufvar(i, "&modifiable")
 if l:count == a:num
 exe "buffer " . i
 return
 endif
 let l:count = l:count + 1
 endif
 endfor
 echo "No buffer!"
endfunction
function! BufPos_Initialize()
 for i in range(1, 9)
 exe "map <M-" . i . "> :call BufPos_ActivateBuffer(" . i . ")<CR>"
 endfor
 exe "map <M-0> :call BufPos_ActivateBuffer(10)<CR>"
endfunction

" From an idea by Michael Naumann
function! VisualSearch(direction) range
    let l:saved_reg = @"
    execute "normal! vgvy"

    let l:pattern = escape(@", '\\/.*$^~[]')
    let l:pattern = substitute(l:pattern, "\n$", "", "")

    if a:direction == 'b'
        execute "normal ?" . l:pattern . "^M"
    elseif a:direction == 'gv'
        call CmdLine("vimgrep " . '/'. l:pattern . '/' . ' **/*.')
    elseif a:direction == 'f'
        execute "normal /" . l:pattern . "^M"
    endif

    let @/ = l:pattern
    let @" = l:saved_reg
endfunction

function! CmdLine(str)
    exe "menu Foo.Bar :" . a:str
    emenu Foo.Bar
    unmenu Foo
endfunction


function! CurDir()
    let curdir = substitute(getcwd(), '/Users/amir/', "~/", "g")
    return curdir
endfunction


func! Cwd()
  let cwd = getcwd()
  return "e " . cwd
endfunc


command! Bclose call <SID>BufcloseCloseIt()
function! <SID>BufcloseCloseIt()
   let l:currentBufNum = bufnr("%")
   let l:alternateBufNum = bufnr("#")

   if buflisted(l:alternateBufNum)
     buffer #
   else
     bnext
   endif

   if bufnr("%") == l:currentBufNum
     new
   endif

   if buflisted(l:currentBufNum)
     execute("bdelete! ".l:currentBufNum)
   endif
endfunction

set autoindent

set smartindent

set tabstop=4

set smarttab
set fdm=manual

set backupdir=~/.vim/backup//
set directory=~/.vim/swap//
set undodir=~/.vim/undo//

filetype plugin on

filetype indent on

noremap <Leader>o <Esc>:CommandT<CR>
noremap <Leader>O <Esc>:CommandTFlush<CR>
noremap <Leader>O <Esc>:CommandTFlush<CR>

let g:tagbar_usearrows = 1
nnoremap <leader>l :TagbarToggle<CR>
