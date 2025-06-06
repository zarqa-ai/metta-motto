!(import! &self motto)
(= (doc joke_struct)
   (Doc
    (type "object")
    (description "joke description")
    (properties
      (item
          (anyOf
              is_array
              (
                  (description "Joke to tell user.")
                  (properties
                    (setup
                      (description "The setup of the joke")
                      (type "string")
                    )
                    (punchline
                      (description "The punchline to the joke")
                      (type "string")
                    )
                    (rating
                      (type "integer")
                      (description "How funny the joke is, from 1 to 10")
                      (default None)
                    )
                  )
                  (type "object")
                  (required is_array setup punchline)
              )
              (
                  (description "Joke that user said.")
                  (properties
                    (punchline
                      (description "The punchline to the joke")
                      (type "string")
                    )
                    (rating
                      (type "integer")
                      (description "How funny the joke is, from 1 to 10")
                      (default None)
                    )
                  )
                  (type "object")
                  (required is_array punchline)
              )
          )
      )
    )
    (required is_array item)
   )
)

!((langhcian-llm-agent) (user "Tell me a joke about cats") (OutputStructure joke_struct))
!((langhcian-llm-agent) (user "I told my computer I needed a break, and now it won’t stop sending me Kit-Kat ads.") (OutputStructure joke_struct))
