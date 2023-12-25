!(extend-py! motto.intents.regex_space)

!(bind! &regex_space (new-regex-space "./data/regex_templates" ))

!(match &regex_space ($intent_name "hello") $intent_name)

