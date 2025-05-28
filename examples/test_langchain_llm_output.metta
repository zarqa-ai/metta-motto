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
                                (default  None)
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
                                (default  None)
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


!(import! &self motto)
(= (doc multiply)
  (Doc
    (description "Multiplies a and b")
    (properties
      (a
        (title 'A')
        (type 'integer')
      )
       (b
        (title 'B')
        (type 'integer')
      )
    )
     (type 'object')
     (required is_array a b)
  )
)

(= (doc multiply_struct)
  (Doc
        (description "shows result of multiplication")
        (properties
          (a
            (description "first value")
            (type 'integer')
          )
           (b
            (description "second value")
            (type 'integer')
          )
          (multiply_result
            (description "result of multiplication")
            (type 'integer')
          )
        )
        (type 'object')
        (required is_array multiply_result)
  )
)


!((langhcian-llm-agent) (user "Tell me a joke about cats") (OutputStructure joke_struct))
!((langhcian-llm-agent) (user "I told my computer I needed a break, and now it won’t stop sending me Kit-Kat ads.") (OutputStructure joke_struct))
!((langhcian-llm-agent) (user "What is  2 * 3?") (Tools multiply ) (OutputStructure multiply_struct))