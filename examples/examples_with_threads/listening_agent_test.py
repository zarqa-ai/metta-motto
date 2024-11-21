from hyperon import *

if __name__ == '__main__':
    m = MeTTa()
    print(m.run('''
      ! (import! &self motto)
      ! (bind! &a1 (listening-agent "simple_call.msa"))
      ! (&a1)
      ! (println! "Agent is running") 
      ! (&a1 .input (py-dict (("message" "who is the 6 president of France") ("additional_info" (py-list ((py-tuple ("model_name" "gpt-3.5-turbo" "String"))))))))
      ! ((py-atom time.sleep) 3)
      ! (&a1 .get_output)
      ! (&a1 .input "who is John Lennon?")
      ! (&a1 .set_canceling_variable True)
      ! ((py-atom time.sleep) 2)
      ! (&a1 .get_output)
      ! (&a1 .stop)
    '''))
