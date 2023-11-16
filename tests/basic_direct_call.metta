!(extend-py! motto)

!(assertEqual
   (llm
     (Agent (echo-agent))
     (Messages (user "Test")))
   ; Single message is unwrapped
   (user "Test")
)

!(assertEqual
   (llm
     (Agent (echo-agent))
     (Messages (system "Ping") (user "Pong")))
   (Messages (system "Ping") (user "Pong"))
)
