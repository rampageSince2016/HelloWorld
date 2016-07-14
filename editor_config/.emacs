;;立即回显命令
(setq echo-keystrokes -1)

;;设置python解析器
(setq elpy-rpc-python-command "~/anaconda34/bin/python")

;;elpy的配置 start
(require 'package)
(add-to-list 'package-archives
			              '("elpy" . "http://jorgenschaefer.github.io/packages/"))
(package-initialize)
(elpy-enable)
;;elpy的配置 end
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(python-check-command "flymake")
 '(python-shell-interpreter "~/anaconda34/bin/ipython"))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
