!(extend-py! motto.sparql_extension.sparql_extension)

;test filters
!(assertEqual
    (filter (not (bound $url)))
    "filter (!(bound($url)))")

!(assertEqual
    (filter (gt $population  15000000))
    "filter ($population > 15000000)")


!(assertEqual
    (filter (or (contains (str $occupation) 'Actor')  (contains (str $occupation) 'Actress')))
    "filter (contains(str($occupation), 'Actor') || contains(str($occupation), 'Actress'))")

!(assertEqual
    (filter (and (gt $date "'1968-10-1'^^xsd:date")  (lt $date "'1968-10-30'^^xsd:date")))
    "filter ($date > '1968-10-1'^^xsd:date && $date < '1968-10-30'^^xsd:date)")

;test fields
!(assertEqual
  (fields ($country_name $population))
  "$country_name $population")

!(assertEqual
    (fields ($manufacturer (as (count $product) $count)))
    "$manufacturer (count($product) as $count)")
;test where
