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
     (required a)
     (required b)
  )
)


(= (doc add)
  (Doc
    (description "Adds a and b.")
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
     (required a)
     (required b)
  )
)

(= (multiply ($a $b) $msgs)
   (* $a $b)
)

(= (add  ($a $b) $msgs)
   (+ $a $b)
)
;default model="gpt-4o-mini", model_provider='openai'
;!((langhcian-llm-agent) (user "What is  2 * 3? What is 2 + 5 ") (Tools multiply add))
!((langhcian-llm-agent "claude-3-opus-20240229" "anthropic") (user "Who is John Lennon?") (Tools multiply add))