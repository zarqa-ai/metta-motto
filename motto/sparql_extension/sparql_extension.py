from hyperon import *
from hyperon.ext import register_atoms
from rdflib import Graph

class ServiceFeatures:
    def __init__(self, service_type):
        self.prefixes = {}
        self.service = ""
        service_type = repr(service_type).lower() if not isinstance(service_type, str) else service_type.lower()
        if service_type == "dbpedia":
            self.prefixes["dbo"] = "<http://dbpedia.org/ontology/>"
            self.prefixes["dbp"] = "<http://dbpedia.org/property/>"
            self.prefixes["dbr"] = "<http://dbpedia.org/resource/>"
            self.prefixes["rdf"] = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#>"
            self.prefixes["rdfs"] = "<http://www.w3.org/2000/01/rdf-schema#>"
            self.prefixes["foaf"] = "<http://xmlns.com/foaf/0.1/>"
            self.prefixes["dc"] = "<http://purl.org/dc/elements/1.1/>"
            self.prefixes["dct"] = "<http://purl.org/dc/terms/>"
            self.prefixes["skos"] = "<http://www.w3.org/2004/02/skos/core#>"
            self.service = "<https://dbpedia.org/sparql>"


class RdfHelper:
    complex_filters = ["filter_exists", "filter_not_exists", "union", "minus"]
    binary_operations_dict = {"+": "+", "-": "-", "*": "*", "/": "*", "=": "=", "!=": "!=", "lt": "<", "gt": ">",
                              "le": "<=", "ge": ">=",
                              "or": "||", "and": "&&", "as": "as"}
    unary_operations_dict = {"not": "!"}

    output_options_functions = ['limit', 'offset', 'group by', 'order by']
    aggregate_functions = ['count', 'sum', 'avg', 'min', 'max', 'groupconcat', 'sample']

    def __init__(self, service_type="dbpedia"):
        self.set_service_type(service_type)

    def set_service_type(self, service_type):
        self.service_type = repr(service_type).lower() if not isinstance(service_type, str) else service_type.lower()
        self.service_features = ServiceFeatures(self.service_type)


    @staticmethod
    def repr_atom(atom) -> str:
        item = repr(atom)
        if len(item) > 2 and item[0] == '"' and item[-1] == '"':
            item = item[1:-1]
        return item

    @staticmethod
    def parse_functions_and_args(atom):
        '''
        :param atom:
        :return: converts expression like  (GT  (count $product) 10)) into next: count($product) > 10
        '''
        if not hasattr(atom, 'get_children'):
            return RdfHelper.repr_atom(atom)
        children = atom.get_children()
        if len(children) > 2:
            # for the case of binary operations like >,<, or, and
            key = RdfHelper.repr_atom(children[0]).lower()
            if key in RdfHelper.binary_operations_dict:
                left = RdfHelper.parse_functions_and_args(children[1])
                right = RdfHelper.parse_functions_and_args(children[2])
                return left + " " + RdfHelper.binary_operations_dict[key] + " " + right
        args = ""
        last = len(children) - 1
        for i in range(last + 1):
            child = children[i]
            if not hasattr(child, 'get_children'):
                key = RdfHelper.repr_atom(child)
                # takes into account unary operations
                args += RdfHelper.unary_operations_dict[
                    key] if key in RdfHelper.unary_operations_dict else RdfHelper.repr_atom(child)
                if i < last:
                    args += "("

            else:
                args += f"{RdfHelper.parse_functions_and_args(child)}"
                if i < last:
                    args += ", "
            if i == last:
                args += ")"
        return args

    @staticmethod
    def __filter_inner(atom):
        '''
        :param atom:
        :return: parses metta style function to sparql function  (contains $item1 $item2)  -> contains($item1, item2)
        '''
        if hasattr(atom, 'get_children'):
            result = RdfHelper.parse_functions_and_args(atom)
        else:
            result = f"({atom})"
        return result


    def filter(self, atom):
        result = RdfHelper.__filter_inner(atom)
        return [ValueAtom(f"filter ({result})")]

    def fields(self, atom):
        result = ""
        if hasattr(atom, 'get_children'):
            for child in atom.get_children():
                if hasattr(child, 'get_children'):
                    result += f"({RdfHelper.parse_functions_and_args(child)}) "
                else:
                    result += f"{child}" + " "
        else:
            result = f"{atom}"
        return [ValueAtom(f"{result.strip()}")]

    def having(self, atom):
        result = RdfHelper.__filter_inner(atom)
        return [ValueAtom(f"Having ({result})")]

    @staticmethod
    def repr_children(atom):
        if hasattr(atom, 'get_children'):
            children = atom.get_children()
            return [RdfHelper.repr_atom(child) for child in children]
        return RdfHelper.repr_atom(atom)

    def where(self, atom, function):
        conditions, _ = self.__get_conditions_from_children(atom)
        result = "WHERE{\n" if function == "where" else "{\n"
        if self.service_features.service:
            result += f"SERVICE {self.service_features.service}" + "{\n"
        result += " .\n".join(conditions) + "}"
        if self.service_features.service:
            result += "}"
        return [ValueAtom(result)]

    def __get_conditions_from_children(self, atom):
        '''

        :param atom:
        :return:  joins triples and another arguments into one string :
        (?craft foaf:name "Apollo 7" ) (  ?craft foaf:homepage ?homepage) ->    {?craft foaf:name "Apollo 7" .   ?craft foaf:homepage ?homepage}
        '''
        conditions = []
        # simple means that function has one argument consisting of one ExpressionAtom
        is_simple = True
        if hasattr(atom, 'get_children'):
            children = atom.get_children()
            for child in children:
                condition = RdfHelper.repr_children(child)
                if isinstance(condition, list):
                    is_simple = False
                    conditions.append(" ".join(condition))
                else:
                    conditions.append(condition)
        return conditions, is_simple

    def collect_conditions(self, atom, function: str):
        function = function.lower()
        if hasattr(atom, 'get_children'):
            conditions, is_simple = self.__get_conditions_from_children(atom)
            if function == "union":
                return [ValueAtom("{{" + "} UNION {".join(conditions) + "}}\n")]
            # if function is limit, order by, offset, ...
            elif function in RdfHelper.output_options_functions:
                return [ValueAtom(f"{function} " + " ".join(conditions))]
            joiner = " . \n" if not is_simple else " "
            return [ValueAtom(f"{function} {{" + joiner.join(conditions) + "}")]
        # order by desc
        elif function == 'order by desc':
            return [ValueAtom(f"{function}({atom})")]
        # limit, group by
        elif function in RdfHelper.output_options_functions:
            return [ValueAtom(f"{function} {atom}")]
        return []



    def execute_query(self, query_atom, function, distinct=False):
        '''

        :param query_atom:
        :param function:
        :param distinct:
        :return: call select, ask or 'describe' query
        '''
        values = []
        try:
            conditions = []
            if hasattr(query_atom, 'get_children'):
                children = query_atom.get_children()
                for child in children:
                    condition = RdfHelper.repr_children(child)
                    conditions.append(" ".join(condition) if isinstance(condition, list) else condition)
            if function == "select" and distinct:
                str_select =  "select distinct"
            else:
                str_select = function
            sparql_query = ""
            for key, prefix in self.service_features.prefixes.items():
                sparql_query += f"PREFIX {key}: {prefix}" + "\n"
            sparql_query += str_select + " " + " ".join(conditions)
            if sparql_query:
                graph = Graph()
                for r in graph.query(sparql_query):
                    row = []
                    if hasattr(r, 'asdict'):
                        for k, v in r.asdict().items():
                            row.append(ValueAtom(v))
                    else:
                        row.append(ValueAtom(r))
                    values.append(ValueAtom(row))
        except Exception as error:
            print(error)
        finally:
            return values


@register_atoms
def sql_space_atoms():
    helper = RdfHelper()

    return {
        r"set-sparql-service-type": G(
            OperationObject('set-sparql-service-type', lambda a: helper.set_service_type(a), unwrap=False)),
        'filter':
            G(OperationObject('filter', lambda a: helper.filter(a), unwrap=False)),
        'union':
            G(OperationObject('union', lambda a: helper.collect_conditions(a, "union"), unwrap=False)),
        'filter_not_exists':
            G(OperationObject('filter_not_exists', lambda a: helper.collect_conditions(a, "filter not exists"),
                              unwrap=False)),
        'minus':
            G(OperationObject('minus', lambda a: helper.collect_conditions(a, "minus"),
                              unwrap=False)),
        'filter_exists':
            G(OperationObject('filter_exists', lambda a: helper.collect_conditions(a, "filter exists"),
                              unwrap=False)),
        'optional':
            G(OperationObject('optional', lambda a: helper.collect_conditions(a, "optional"), unwrap=False)),
        'where':
            G(OperationObject('where', lambda a: helper.where(a, "where"), unwrap=False)),
        'conditions':
            G(OperationObject('conditions', lambda a: helper.where(a, "conditions"), unwrap=False)),
        'fields':
            G(OperationObject('fields', lambda a: helper.fields(a), unwrap=False)),
        'limit':
            G(OperationObject('limit', lambda a: helper.collect_conditions(a, "limit"), unwrap=False)),
        'offset':
            G(OperationObject('offset', lambda a: helper.collect_conditions(a, "offset"), unwrap=False)),
        'order_by':
            G(OperationObject('order_by', lambda a: helper.collect_conditions(a, "order by"), unwrap=False)),
        'order_by_desc':
            G(OperationObject('order_by_desc', lambda a: helper.collect_conditions(a, "order by desc"), unwrap=False)),
        'select':
            G(OperationObject('select', lambda a: helper.execute_query(a, "select"), unwrap=False)),
        'ask':
            G(OperationObject('ask', lambda a: helper.execute_query(a, "ask"), unwrap=False)),

        'describe':
            G(OperationObject('describe', lambda a: helper.execute_query(a, "describe"), unwrap=False)),

        'select_distinct':
            G(OperationObject('select_distinct', lambda a: helper.execute_query(a, "select", True), unwrap=False)),
        'group_by':
            G(OperationObject('group_by', lambda a: helper.collect_conditions(a, "group by"), unwrap=False)),
        'having':
            G(OperationObject('having', lambda a: helper.having(a), unwrap=False)),

    }
