!(import! &self motto)
(= (doc get_current_weather)
 (Doc
   (description "Get the current weather for the city")
   (parameters
     (location "the city: " ("Tokyo" "New York" "London"))
   ))
)

(= (get_current_weather ($arg) $msgs)
  (if (== (contains-str $arg "Tokyo") True)
      "the temperature in Tokyo is 75 fahrenheit"
      (if (== (contains-str $arg "New York") True)
          "The temperature in New York is 80 fahrenheit"
          (concat-str (concat-str "The temperature in " $arg) " is 70 fahrenheit" )
      )
 )
)

!((chat-gpt-agent "gpt-3.5-turbo")
  (user "What is the current weather in London ?")
  (Function get_current_weather)
)

