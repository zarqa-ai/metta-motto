!(import! &self motto)
!(import! &self  snet_io)
!(bind! &agent1
    (
     snet-sdk-agent naint paraphrase-generation
          ;set method name and parameters for it
         (py-dict ((method paraphrase) (sentence (query))))
         (py-dict ((free_call_auth_token_bin
          "35c9a13282fb034f8caafae26910d0e9fe6e8e237df73fe9d999df8386df339408cd75c93d759f2ad5848d31005cd48e9b4257908f5cbce05b2de6aa8f929d941b")
          (free_call_token_expiry_block 20922454))
         )
    )
)
!(&agent1 (user  "To be, or not to be, that is the question"))
!(&agent1 (user  "Nikola Tesla was a Serbian-American inventor, electrical engineer, mechanical engineer, and futurist"))