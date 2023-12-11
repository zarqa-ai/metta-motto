!(extend-py! motto)
!(bind! &retrieval (Agent (retrieval-agent "text_for_retrieval.txt" 200 2 "data")))
!(llm  &retrieval (user "Can I publish service without using grpc?" ))
