from hyperon import MeTTa, ValueAtom, S
from motto.agents import Agent, Response


def test_filter():

    m = MeTTa()
    m.load_py_module('motto.sparql_extension.sparql_extension')
    assert m.run('''
        !(filter (not (bound $url)))
    ''') == [[ValueAtom("filter (!(bound($url)))")]]
