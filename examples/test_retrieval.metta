; This is an old example, which doesn't use prompt templates and agents.
; It also composes messages and llm execution in a functional way.
; Thus, it is not a canonical (but still valid) way of using motto.


!(extend-py! motto)
!(bind! &retrieval (Agent (retrieval-agent "text_for_retrieval.txt")))
!(llm  &retrieval (user "Can I publish service without using grpc?" ) (docs_count 1))
