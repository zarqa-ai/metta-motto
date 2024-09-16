!(import! &self motto)
!(bind! &agent1
    (
     snet-sdk-agent naint paraphrase-generation
          ;set method name and parameters for it
         (py-dict ((method paraphrase) (sentence (query))))
    )
)
!(&agent1 (user  "To be, or not to be, that is the question"))
!(&agent1 (user  "Nikola Tesla was a Serbian-American inventor, electrical engineer, mechanical engineer, and futurist"))