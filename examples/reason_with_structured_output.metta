!(import! &self motto)

; This is another PoC example of LLM-MeTTa interoperability

; Here, we have a set of statements in natural language
(Fact "Sam is a frog")
(Fact "Any frog is not a helicopter")
(Fact "Any alien likes helicopter")
(Fact "Arilou is an alien")
(Fact "Tom is a helicopter")

; Statements are processed into a functional form for the sake of simplicity -
; no full-fledged reasoning engine is used, so the example is limited.

; The function to retrieve results
(= (whom $what $A)
   (if (and ($what $A $C) ($C $B))
       $B (empty)))

!(bind! &agent (metta-agent "06b_reason_with_structured_output.msa"))

; represent $fact as metta expression
!(match &self (Fact $fact)
    (let* (((quote $expr) (&agent (user $fact)))
           (() (println! ($fact Adding: (quote $expr))))) ; print what is added
        (add-atom &self $expr)
    )
)
;!(likes helicopter "Arilou")

;not every call returns correct result
!(let (quote $a) (&agent (user "John is an alien")) (add-atom &self $a))
!(unquote (&agent (user "Does John likes helicopter?")))

!(unquote (&agent (user "Is Tom a helicopter?")))
!(unquote (&agent (user "Is Sam a frog?")))
