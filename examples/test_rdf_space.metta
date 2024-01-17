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

; Display names and dates of birth of all actors born in London after year 1930. who are still alive
!(match &rdf_space (, ($person dbo:birthPlace dbr:London) ($person dbo:occupation dbr:Actor) ($person foaf:name $name)
($person dbo:birthDate $birth)
(filter ($birth > "'1930-01-01'^^xsd:date"))
(filter_not_exists ($person dbo:deathDate $death))  (limit 3)) ($name $birth))


!(match &rdf_space (, ($city dbp:populationTotal $popTotal) ($city rdfs:label $name)
(optional ($city dbp:populationMetro $popMetro) )
(filter ($popTotal > 50000))
(union (($city rdf:type "<http://dbpedia.org/class/yago/WikicatCitiesInTexas>")
($city rdf:type "<http://dbpedia.org/class/yago/CitiesInCalifornia>")))(limit 3) (offset 2)) ($city $popTotal $popMetro $name ))
