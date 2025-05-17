!(import! &self motto)

(= (has_flue $x)
    (case (match &self (, (has_symptom $x fever) (has_symptom $x cough) (has_symptom $x fatigue)) $x)
        (
            ($x True)
            ($  False)
        )
     )
)

(= (has_measles $x)
    (case (match &self (, (has_symptom $x  rash) (has_symptom $x fever)) $x)
        (
            ($x True)
            ($  False)
        )
     )
)


;(has_symptom John fever)
;(has_symptom John cough)
;(has_symptom John fatigue)
;(has_symptom Mary rash)
;(has_symptom Mary fever)
;(has_symptom Amy rash)


;!(has_flue John)
;!(has_measles Mary)
;!(has_measles John)
;!(has_measles amy)


( = (add_symptoms $name $symptoms)
   (let* (($tail  (cdr-atom $symptoms))  ($sympt (car-atom $symptoms)))
        (if (== $tail ())
            (add-atom &self (has_symptom $name $sympt))
            (let () (add-atom &self (has_symptom $name $sympt)) (add_symptoms $name $tail))
        )
   )
)

!(bind! &llm_agent (metta-agent "selected_examples/symptoms_extractor.msa"))
!(&llm_agent  (user "Alan is holding a fever, also he has a rash"))
!(has_measles Alan)