!(extend-py! motto)

; The script imported this way will be executed only once,
; but if it is a passive script (without ! commands), its
; content can be reused
!(import! &script basic_script.mps)

(= (user-query) "Hello world.")

!(assertEqual (llm &script)
"user Hello world.
assistant Hi there")

!(remove-atom &self (= (user-query) "Hello world."))
(= (user-query) "Bye")
!(assertEqual (llm &script)
"user Bye
assistant Bye")
