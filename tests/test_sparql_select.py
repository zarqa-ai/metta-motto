from hyperon import MeTTa, ValueAtom, G
from motto.agents import Agent, Response


def test_filter():

    m = MeTTa()
    m.load_py_module('motto.sparql_extension.sparql_extension')
    result =  m.run('''
        !(select ( (fields ($name $birth)) (where (($person dbo:birthPlace dbr:London) ($person dbo:birthDate $birth)
    ($person dbp:name $name)
    (filter (= (lang $name) 'en'))
    (optional ($person dbo:deathDate $death ))
    (filter (and (GT $birth "'1900-01-01'^^xsd:date")  (LT $birth "'1950-01-01'^^xsd:date")))))
       (order_by ($birth))(limit 1)))
    ''', True)
    for res in result:
        assert repr(res) == '["Phil Scott", "1900-01-03"]'
    # assert result == [G(["Phil Scott", "1900-01-03"]),
    #          G(["Harry Kernoff""1900-01-09"]),
    #          G(["Violette Cordery", "1900-01-10"])]
