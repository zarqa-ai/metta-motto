!(extend-py! motto)

(= (doc func_test)
   (Doc
     (description "call-me")
     (parameters
      (arg "argument=" (A B C D))
     ))
)
; This is another limitation: LLM output should somehow be transormed to MeTTa expressions
(= (func_test ("A") $msgs)
   "SUCCESS")

!(assertEqual
  (llm
    (Agent EchoAgent)
    (user "Please execute call-me with argument=A")
    (function func_test))
  "SUCCESS")
