!(extend-py! motto.llm_gate)

; We can call ChatGPT Agent from MeTTa as well using generic llm function
! (llm (Agent (chat-gpt)) (user "Hello"))
! (llm (Agent (chat-gpt))
  (Messages (assistant "Hello") (user "Hello")))

; We can also pass function call to ChatGPT from MeTTa.
; It is done via providing a function doc in a special format.
(= (doc func)
   (Doc
     (description "Call this function to respond every user question")
     (parameters
       (user_query "user utterance")
     ))
)
; A dummy function just to show it is called
(= (func ("What is my name?") $msgs)
   "I don't know!")

; The result of llm will be a MeTTa expression, which will be evaluated further
!(llm (Agent (chat-gpt))
  (Messages (system "Always perform the function call")
            (user "What is my name?"))
  (Functions func))

; It can remain unreduced as well
!(llm (Agent (chat-gpt))
  (Messages (system "Always perform the function call")
            (user "What is my surname?"))
  (Functions func))
