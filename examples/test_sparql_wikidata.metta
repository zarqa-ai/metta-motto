!(extend-py! motto.sparql_gate)
!(set-sparql-service-type "wikidata")
;People who were born in Berlin before 1900
;sparql query to wikidata which lists names and places of birth of all Nobel laureates in literature over the past 10 years



!(select ((fields ($laureateLabel $placeOfBirthLabel $when)) (where (($laureate p:P166 $event) ($laureate wdt:P1559 $laureateLabel)
($laureate  wdt:P19 ?placeOfBirth) ($event ps:P166 wd:Q37922 ) ($placeOfBirth wdt:P1705 $placeOfBirthLabel)
($event pq:P585 $when) (filter (>= (year $when) (- (year (now)) 10))))) (order_by $when)))
