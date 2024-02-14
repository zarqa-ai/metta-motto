!(extend-py! motto)
!(extend-py! motto.sparql_gate)
!(set-sparql-service-type "wikidata")
(llm (Agent 10_generate_query_wikidata.msa)(user "Select US presidents and their wives"))
;result
(select ((fields ($president $presidentLabel $wife $wifeLabel))
(where (($president wdt:P31 wd:Q5) ($president wdt:P39 wd:Q11696) ($president wdt:P27 wd:Q30)
($president wdt:P26 $wife)) (service (wikibase:label (bd:serviceParam wikibase:language "'en'"))))))
;correct result
(select ((fields ($president $presidentLabel $wife $wifeLabel)) (where (($president wdt:P31 wd:Q5) ($president wdt:P39 wd:Q11696)
($president wdt:P27 wd:Q30) ($president wdt:P26 $wife) (service (wikibase:label (bd:serviceParam wikibase:language "'en'")))))))

(llm (Agent 10_generate_query_wikidata.msa)(user "Select number of musicians born in the US  after 1984 year and before 1988"))
;result
(select ((fields ((as (count $musician) $count)))) (where (($musician wdt:P106 wd:Q639669) ($musician wdt:P569 $dob)
($musician wdt:P27 wd:Q30) (filter (and (> (year $dob) 1984) (< (year $dob) 1988)))
(service (wikibase:label (bd:serviceParam wikibase:language "'en'"))))))
;correct result
(select ((fields ((as (count $musician) $count))) (where (($musician wdt:P31 wd:Q5) ($musician wdt:P106 wd:Q639669)
($musician wdt:P569 $dob) ($musician wdt:P19 $placeofbirh) ($placeofbirh  wdt:P17 wd:Q30)
(filter (and (> (year $dob) 1984) (< (year $dob) 1988)))))))

(llm (Agent 10_generate_query_wikidata.msa)(user "When did John Lennon die?"))
;result
(select ((fields ($dateOfDeathLabel)) (where (($person rdfs:label "'John Lennon'@en")
 ($person wdt:P570 $dateOfDeath) (service (wikibase:label (bd:serviceParam wikibase:language "'en'")))))))

(llm (Agent 10_generate_query_wikidata.msa)(user "Display names of actors born in Australia after 1990"))
;result
(select ((fields ($actorLabel))
    (where
        (($actor wdt:P106 wd:Q33999) ($actor wdt:P569 $dob)
        ($actor wdt:P27 wd:Q408) (filter (> (year $dob) 1990 ))
        (service (wikibase:label (bd:serviceParam wikibase:language "'en'")))
        )
    )
))

(llm (Agent 10_generate_query_wikidata.msa)(user "Show US Republican politicians over 70 years of age and who are still alive. "))
; result is the same as correct result but not includes ($politician wdt:P102 wd:Q29468 )
;correct result
(select ((fields ($politician $politicianLabel))
        (where
            (($politician wdt:P106 wd:Q82955) ($politician wdt:P569 $dob)
            ($politician wdt:P27 wd:Q30)
	        ($politician wdt:P102 wd:Q29468 )
            (filter (> (year $dob) (- (year (now)) 70)))
            (filter_not_exists ($politician wdt:P570 $death))
            (service (wikibase:label (bd:serviceParam wikibase:language "'en'")))
            )
        )
 ))

(llm (Agent 10_generate_query_wikidata.msa)(user "Select all writers names from Switzerland and also select theirs birthplaces"))
;result
(select ((fields ($writerLabel $birthplaceLabel))
        (where
            (($writer wdt:P31 wd:Q5) ($writer wdt:P27 wd:Q39) ($writer wdt:P106 wd:Q36180) ($writer wdt:P19 $birthplace))
            (service (wikibase:label (bd:serviceParam wikibase:language "'en'")))
        )
    ))

(llm (Agent 10_generate_query_wikidata.msa)(user "Display names of all capital cities that are in the CET time zone.
Sort the results based on the size of the population of the capitals from the result set"))
;result
(select ((fields ($capitalLabel))
        (where
            (($capital wdt:P31 wd:Q5119) ($capital wdt:P17 wd:Q30) ($capital wdt:P421 wd:Q1891)
            ($capital wdt:P1082 $population))
            (service (wikibase:label (bd:serviceParam wikibase:language "'en'")))
        ))
        (order_by desc ($population)))
;correct result
(select ((fields ($capitalLabel))
    (where
        (($capital wdt:P31 wd:Q5119)  ($capital wdt:P421 wd:Q25989) ($capital wdt:P1082 $population)
        (service (wikibase:label (bd:serviceParam wikibase:language "'en'"))))
    )
    (order_by $population)
))
(llm (Agent 10_generate_query_wikidata.msa)(user "List of all albums by musician Pharrell Williams"))
;result
(select ((fields ($albumLabel))
        (where
            (($musician wdt:P31 wd:Q215380) ($musician wdt:P175 $album))
            ($album wdt:P31 wd:Q482994)
            ($album wdt:P175 $musician)
            (service (wikibase:label (bd:serviceParam wikibase:language "'en'")))
        )
    ))
; correct result
(select ((fields ($albumLabel))
        (where
            (( $album wdt:P175 wd:Q14313)
            ($album wdt:P31 wd:Q482994)
            (service (wikibase:label (bd:serviceParam wikibase:language "'en'"))))
        )
    ))

(llm (Agent 10_generate_query_wikidata.msa)(user "Where was Edvard Munch born?"))
;result
(select ((fields ($placeOfBirthLabel))
        (where
            (($person wdt:P31 wd:Q5) ($person rdfs:label "'Edvard Munch'@en") ($person wdt:P19 $placeOfBirth))
            (service (wikibase:label (bd:serviceParam wikibase:language "'en'")))
        )
    ))
;correct result
(select ((fields ($placeOfBirthLabel))
        (where
            (($person wdt:P31 wd:Q5) ($person rdfs:label "'Edvard Munch'@en") ($person wdt:P19 $placeOfBirth)
            (service (wikibase:label (bd:serviceParam wikibase:language "'en'")))
        ))
    ))

!(llm (Agent 10_generate_query_wikidata.msa)(user "Tell me Michael Jordan's draft year and the name of the draft team."))