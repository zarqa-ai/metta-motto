!(extend-py! motto)

; Prompt templates should be first loaded into a space
!(import! &prompt 04_prompt_template.mps)
; and then this space should be passed to `llm`,
; possibly together with other parameters
(llm &prompt (user "Compose an adventure about Flatland"))

; Since prompt templates are just spaces treated as parameters to llm,
; they can be created and filled in directly, but this is rarely needed.
!(bind! &space (new-space))
!(add-atom &space (system "Output the user utterance backward"))
!(add-atom &space (user "Window"))
!(llm &space)