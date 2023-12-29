!(extend-py! motto)
!(bind! &regex-agent (regex-agent "./data/data_for_regex/intents/hello_regex.msa" "./data/data_for_regex/responses/intents_responses.msa"))
!(llm (Agent &regex-agent) (user "Hello"))


