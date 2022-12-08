;;; ws-chat-gpt.el --- Plugin ChatGPT for websocket bridge.  -*- lexical-binding: t; -*-

;; Copyright (C) 2022  Qiqi Jin

;; Author: Qiqi Jin <ginqi7@gmail.com>
;; Keywords: lisp

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <https://www.gnu.org/licenses/>.

;;; Commentary:

;;

;;; Code:
(require 'websocket-bridge)

(defgroup
  ws-chat-gpt()
  "Check grammar in buffers by chat-gpt."
  :group 'applications)

(defcustom ws-chat-gpt-debug t
  "If open debug mode.
default is nil.
t will open debug mode, the python code will show playwright window.
Because Chromium headless and headful have diferent behave, so current version open debug mode in default.")

(defvar ws-chat-gpt-py-path
  (concat (file-name-directory load-file-name) "ws_chat_gpt.py"))


(defun ws-chat-gpt-start ()
  "Start websocket bridge chat-gpt."
  (interactive)
  (websocket-bridge-app-start "chat-gpt" "python3" ws-chat-gpt-py-path))


(defun ws-chat-gpt-restart ()
  "Restart websocket bridge chat-gpt and show process."
  (interactive)
  (websocket-bridge-app-exit "chat-gpt")
  (ws-chat-gpt-start)
  (websocket-bridge-app-open-buffer "chat-gpt"))

(defun ws-chat-gpt-input ()
  "Send input to chatGPT."
  (interactive)
  (ws-chat-gpt-send-request "input"
                            (read-string
                             (format "Tell chatGPT: (%s): "
                                     (thing-at-point 'line))
                             nil
                             nil
                             (thing-at-point 'line))))

(defun ws-chat-gpt-send-request (func-name &optional parameter)
  "Send request to chatGPT, with FUNC-NAME PARAMETER."
  (websocket-bridge-call "chat-gpt" func-name parameter))

(defun ws-chat-gpt-refresh()
  "Refresh ChatGPT page."
  (interactive)
  (ws-chat-gpt-send-request "refresh"))

(defun ws-chat-gpt-render (html)
  "Called by python, to render HTML.
HTML is the chatGPT resutl."
  (pop-to-buffer "*chatGPT*")
  (setq buffer-read-only nil)
  (erase-buffer)
  (shr-insert-document
   (with-temp-buffer
     (insert html)
     (libxml-parse-html-region (point-min) (point-max))))
  (goto-char (point-min))
  (special-mode))

(provide 'ws-chat-gpt)
;;; ws-chat-gpt.el ends here
