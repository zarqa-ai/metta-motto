!(import! &self motto)
! (bind! &a1 (listening-agent "examples/examples_with_threads/simple_call.msa"))
! (&a1 (user "hi"))
! (println! "Agent is running")
! (&a1 .input "who is the 6 president of France")
! ((py-atom time.sleep) 3)
! (&a1 .get_output)
! (&a1 .input "who is John Lennon?")
! (&a1 .set_canceling_variable True)
! ((py-atom time.sleep) 3)
! (&a1 .get_output)
! (&a1 .stop)