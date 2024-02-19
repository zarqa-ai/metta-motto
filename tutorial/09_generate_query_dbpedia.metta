!(import! &self motto)
!(llm (Agent 09_generate_query_dbpedia.msa)
(user "Display names of all capital cities that are in the CET time zone. Sort the results based on the size of the population of the capitals from the result set."))

;result
(select ((fields ($capital $population)) (where (($capital a dbo:City) ($capital dbo:country ?country)
($country dbo:capital $capital) ($capital dbo:timeZone "<http://dbpedia.org/resource/Central_European_Time>")
($capital dbo:populationTotal $population))) (order_by_desc $population)))


!(llm (Agent 09_generate_query_dbpedia.msa)
(user "Select all writers names  from Switzerland and also select  theirs birthplaces"))

;result
(select ((fields ($writer $birthplace)) (where (($writer a dbo:Writer)
($writer dbo:birthPlace "<http://dbpedia.org/resource/Switzerland>") ($writer dbo:birthPlace $birthplace)))))


