!(extend-py! motto)

(= (user-query) "Hi there")
(= (task) ORDER)

; user-query and task are not accessible during import!
; and are kept as symbols
!(import! &script nested_script_main.mps)

; they are resolved by llm-gate in the call
!(assertEqual
   (llm (Agent EchoAgent) &script)
"system Help the user with lunch order
user Hi there")
