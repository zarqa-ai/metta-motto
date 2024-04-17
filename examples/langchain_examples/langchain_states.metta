!(let $tools (new-state "[list of tools]")
   (add-atom &self (= (langchain-tools) $tools))
 )


!(let $model (new-state "gpt-3.5-turbo-0125")
    (add-atom &self (= (gtp-model-name) $model))
)

(= (get-langchain-tools)
   (get-state (langchain-tools))
)

(= (set-langchain-tools $tools)
   (change-state! (langchain-tools) $tools)
)

(= (get-gpt-model)
   (get-state (gtp-model-name))
)

(= (set-gpt-model $model)
   (change-state! (gtp-model-name) $model)
)