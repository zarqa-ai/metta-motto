
!(let $model (new-state ((py-atom langchain_openai.ChatOpenAI) (Kwargs (model "gpt-3.5-turbo-0125") (temperature 0))))
    (let () (add-atom &self (= (langchain-model) $model)) (empty))
)

!(let $history (new-state (py-list))
    (let () (add-atom &self (= (langchain-history) $history)) (empty))
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


; functions for langchain tools
(= (get-chat-prompt)
    ((py-dot (py-atom langchain_core.prompts.ChatPromptTemplate) from_messages) (py-list
        (py-atom "('system', 'You are a helpful assistant.')")
        (py-atom "('placeholder', '{chat_history}')")
        (py-atom "('user', '{input}')")
        ((py-atom langchain_core.prompts.MessagesPlaceholder) (Kwargs (variable_name "agent_scratchpad")))
    ))
)
( = (get-langchain-agent $langchain-tools)
     ((py-atom langchain.agents.create_openai_tools_agent) (get-langchain-model)
        (Kwargs (tools  $langchain-tools) (prompt (get-chat-prompt)))
     )
)

;create agent executor and save
!(let $executor (new-state None)
   (let ()  (add-atom &self (= (langchain-agent-executor) $executor)) (empty))
 )

(= (get-langchain-agent-executor)
   (get-state (langchain-agent-executor))
)

(= (set-langchain-agent-executor $langchain-tools)
    (let ()
        (
            (change-state! (langchain-agent-executor)
                (
                    (py-atom langchain.agents.AgentExecutor)
                    (Kwargs (agent (get-langchain-agent $langchain-tools)) (tools $langchain-tools))
                )
            )
        )
    (empty))
)

