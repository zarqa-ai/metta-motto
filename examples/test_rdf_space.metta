!(extend-py! motto.rdf_space.rdf_space)
!(bind! &rdf_space (new-rdf-space dbpedia))

;People who were born in Berlin before 1900
;http://sites.linkeddata.center/help/devop/examples/sparql-examples

!(match &rdf_space (, ($person dbo:birthPlace dbr:Berlin) ($person dbo:birthDate $birth) ($person foaf:name $name)
($person dbo:deathDate $death) (filter ($birth < "'1900-01-01'^^xsd:date"))  (order_asc ($name $birth))
(limit 3)) ($name $birth $death $person ))

; Soccer players, who are born in a country with more than 10 million inhabitants,
; who played as goalkeeper for a club that has a stadium with more than 30.000 seats and the club country is different from the birth country
; http://sites.linkeddata.center/help/devop/examples/sparql-examples

!(match &rdf_space (, ($soccerplayer a dbo:SoccerPlayer)
($soccerplayer  dbo:position "<http://dbpedia.org/resource/Goalkeeper_(association_football)>")
($soccerplayer  dbp:position "<http://dbpedia.org/resource/Goalkeeper_(association_football)>")
($soccerplayer dbo:birthPlace/dbo:country* $countryOfBirth)
($soccerplayer dbo:team $team)
($team dbo:capacity $stadiumcapacity)
($team dbo:ground $countryOfTeam)
($countryOfBirth a dbo:Country)
($countryOfBirth dbo:populationTotal $population)
($countryOfTeam a dbo:Country)
(filter ($countryOfTeam != $countryOfBirth))
(filter ($stadiumcapacity > 30000)) (filter ($population > 10000000)) (limit 3) (distinct True) (order_asc ( $soccerplayer)))
($soccerplayer $countryOfBirth $team $countryOfTeam $stadiumcapacity ))

;Display names and dates of birth of all actors born in London after year 1930. who are still alive
;http://ai.fon.bg.ac.rs/wp-content/uploads/2016/10/SPARQL-examples-2016-eng.pdf
!(match &rdf_space (, ($person dbo:birthPlace dbr:London) ($person dbo:occupation dbr:Actor) ($person foaf:name $name)
($person dbo:birthDate $birth)
(filter ($birth > "'1930-01-01'^^xsd:date"))
(filter_not_exists ($person dbo:deathDate $death))  (limit 3)) ($name $birth))

;Display names and dates of birth of all actors born in London after year 1930. who are still alive
;takes into account cases where the occupation is given as a plain string
;filters with sparql functions are in quotes
!(match &rdf_space (, ($person dbo:birthPlace dbr:London) ($person foaf:name $name)
(union (($person dbo:occupation dbr:Actor)  (($person dbp:occupation $occupation)
(filter ("contains(str($occupation), 'Actor')" || "contains(str($occupation), 'Actress')" ) ))))
($person dbo:birthDate $birth)
(filter ($birth > "'1930-01-01'^^xsd:date"))
(filter_not_exists ($person dbo:deathDate $death))  (limit 3)) ($name $birth))

;Display names of all capital cities that are in the CET time zone.
;Sort the results based on the size of the population of the capitals from the result set.
;http://ai.fon.bg.ac.rs/wp-content/uploads/2016/10/SPARQL-examples-2016-eng.pdf

;(filter ($name = "'en'"))
!(match &rdf_space (, ($country rdf:type dbo:Country ) ($country dbo:capital $city)
($city rdfs:label $name) ($city dbo:populationTotal $population)
(filter_not_exists ( union (($country dbo:dissolutionDate $endDate) ($country dbo:dissolutionYear $endDate)) ))
(union (($city dbo:timeZone dbr:Central_European_Time) (($city dbp:timezone $timezone)  (filter ($timezone = "'CET'")))))
(limit 3)  (order_desc ( $population))) ( $name $city $population))


;Display names and dates of birth and death of all people born in
;London between 1900-1950; sort the results based on the birth date
!(match &rdf_space (, ($person dbo:birthPlace dbr:London) ($person dbo:birthDate $birth)
($person rdfs:label $name)
(filter ("lang($name)" = "'en'"))
(optional ($person dbo:deathDate $death ))
(filter (($birth > "'1900-01-01'^^xsd:date")  && ($birth < "'1950-01-01'^^xsd:date")))
  (limit 3) (order_asc ($birth))) ($name $birth))


PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
SELECT ?manufacturer (COUNT(?product) AS ?count)
WHERE {
?product rdf:type <http://dbpedia.org/ontology/Device> ;
dbpedia-owl:manufacturer ?manufacturer .
}
GROUP BY ?manufacturer
HAVING (COUNT(?product) > 10

!(match &rdf_space (, ($product rdf:type <http://dbpedia.org/ontology/Device>)
($product dbpedia-owl:manufacturer $manufacturer)
(aggregate  (count $product $count))
 (group_by $manufacturer)) ($count $birth))




