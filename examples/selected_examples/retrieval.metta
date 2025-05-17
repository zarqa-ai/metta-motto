!(import! &self motto)
!(bind! &retrieval_agent (retrieval-agent "./data/texts_for_retrieval" 200 2 "data"))
!(&retrieval_agent
     (user "Who made significant advancements in the fields of electromagnetism?"))
!((&retrieval_agent (Kwargs (doc_name "story1.txt")))
     (user  "Who made significant advancements in the fields of electromagnetism?"))


;Here the chunks size is equal to 200, and number of closest chunks to
