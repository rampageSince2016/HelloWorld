(require 'package)

(add-to-list 'package-archives '("melpa" . "http://melpa.org/packages/") t)
(add-to-list 'package-archives '("marmalade" . "https://marmalade-repo.org/packages/"))

(package-initialize)
(when (not package-archive-contents)
    (package-refresh-contents))

(setq
   python-shell-interpreter "ipython"
    python-shell-interpreter-args ""
	 python-shell-prompt-regexp "In \\[[0-9]+\\]: "
	  python-shell-prompt-output-regexp "Out\\[[0-9]+\\]: "
	   python-shell-completion-setup-code
	      "from IPython.core.completerlib import module_completion"
		   python-shell-completion-module-string-code
		      "';'.join(module_completion('''%s'''))\n"
			   python-shell-completion-string-code
			      "';'.join(get_ipython().Completer.all_completions('''%s'''))\n")
