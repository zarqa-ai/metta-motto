!(let $tools (new-state "[list of tools]")
   (let ()  (add-atom &self (= (langchain-tools) $tools)) (empty))
 )

!(let $model (new-state ((py-atom langchain_openai.ChatOpenAI) (Kwargs (model "gpt-3.5-turbo-0125") (temperature 0))))
    (let () (add-atom &self (= (langchain-model) $model)) (empty))
)

!(let $history (new-state (py-list))
    (let () (add-atom &self (= (langchain-history) $history)) (empty))
)

(= (get-langchain-tools)
   (get-state (langchain-tools))
)

(= (set-langchain-tools $tools)
   (let ()  (change-state! (langchain-tools) $tools) (empty))
)

(= (get-langchain-model)
   (get-state (langchain-model))
)

(= (set-langchain-model $model)
   (let () (change-state! (langchain-model) $model) (empty))
)



(= (get-langchain-history)
   (get-state (langchain-history))
)

(=(message2tuple $message) (py-tuple (car-atom $message) (let $a (cdr-atom $message) (car-atom $a) )))

(= (add-langchain-history $history)

        (let () ((py-dot (get-langchain-history) append)   (message2tuple $history)) (empty))
)

(= (clear-langchain-history)
        (let () (change-state! (langchain-history)  (py-list)) (empty))
)