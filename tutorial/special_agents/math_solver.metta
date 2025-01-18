!(import! &self motto)
!(bind! &chat (dialog-agent special_agents/math_solver.msa))
!(&chat (user "Who is John Lennon?"))
;!(&chat (user "How do I solve 3*x^2 - 7*x - 1.25 = 0?"))
;!(&chat (user "Find the probability of getting a numbered card when a card is drawn from the pack of 52 cards."))
;!(&chat (user "Find the limit of (x^3 + 4*x^2 - 3) if x-> c"))
!(&chat (Messages (user "Find the limit of") (media (get-media-message "special_agents/limit_example.png"))))



