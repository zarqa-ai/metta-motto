from hyperon import *
from hyperon.ext import register_atoms
from rdflib import Graph


def results2bindings(vars, values):
    new_bindings_set = BindingsSet.empty()
    if len(values) == 0 or len(vars) != len(values[0]):
        return new_bindings_set

    for value in values:
        bindings = Bindings()
        for i in range(len(vars)):
            bindings.add_var_binding(vars[i], ValueAtom(str(value[i])))
        new_bindings_set.push(bindings)

    return new_bindings_set


class QueryItems:
    def __init__(self, str_items, variables):
        self.str_items = str_items
        self.variables = variables

    @classmethod
    def from_atoms(cls, items):
        str_items = []
        variables = set()
        for i in items:
            if hasattr(i, 'get_children'):
                inner_items = i.get_children()
                if len(inner_items) > 1:
                    q_item = cls.from_atoms(inner_items)
                    str_items.extend(q_item.str_items)
                    variables.union(q_item.variables)
                    continue
            item = repr(i)
            if len(item) > 2 and item[0] == '"' and item[-1] == '"':
                item = item[1:-1]
            if len(item) > 1 and item[0] == "$":
                item = item[1:]
                if item not in variables:
                    variables.add(item)
                item = f"?{item}"

            str_items.append(item)

        return cls(str_items, variables)

class SPARQLComponents:
    def __init__(self):
        self.conditions = []
        self.filters = []
        self.filter_not_exists = []
        self.limit = ""
        self.variables = set()
        self.distinct = False
        self.order_asc = []
        self.order_desc = []
        self.union = []
        self.optional = []
        self.offset = ""


class ServiceFeatures:
    def __init__(self, service_type):
        self.prefixes = {}
        self.service = ""
        service_type = repr(service_type).lower()
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

    @staticmethod
    def get_fields_and_conditions(query_atom):
        ''' parse sql query and get columns to select and conditions for filtering '''
        atoms = query_atom.get_children()

        query_components = SPARQLComponents()
        optional_query_components = []
        for atom in atoms:
            if isinstance(atom, ExpressionAtom):
                items = atom.get_children()
                if len(items) == 3:
                    query_item = QueryItems.from_atoms(items)
                    query_components.conditions.append(" ".join(query_item.str_items))
                    query_components.variables = query_components.variables.union(query_item.variables)
                elif len(items) == 2:
                    first = repr(items[0]).lower()
                    query_item = QueryItems.from_atoms(items[1:])
                    if first == "filter":
                        query_components.filters.append(" ".join(query_item.str_items))
                        query_components.variables = query_components.variables.union(query_item.variables)
                    elif first == "filter_not_exists":
                        query_components.filter_not_exists.append(" ".join(query_item.str_items))
                        query_components.variables = query_components.variables.union(query_item.variables)
                    elif first == "limit":
                        query_components.limit = repr(items[1])
                    elif first == "offset":
                        query_components.offset = repr(items[1])
                    elif first == "distinct":
                        query_components.distinct = "true" in repr(items[1]).lower()
                    elif first == "order_asc":
                        query_components.order_asc.extend(query_item.str_items)
                    elif first == "order_desc":
                        query_components.order_desc.extend(query_item.str_items)
                    elif first == "optional":
                        s = RdfHelper.get_fields_and_conditions(E(items[1]))
                        query_components.optional.append(s)
                        query_components.variables = query_components.variables.union(s.variables)
                    elif first == "union":
                        if hasattr(items[1], 'get_children'):
                            children = items[1].get_children()
                            components = []
                            for child in children:
                                s = RdfHelper.get_fields_and_conditions(E(child))
                                components.append(s)
                                query_components.variables = query_components.variables.union(s.variables)
                            query_components.union.append(components)
                    else:
                        raise ValueError(f"Unexpected query item")
        return query_components


class RdfSpace(GroundingSpace):
    def __init__(self, dbtype):
        super().__init__()
        self.service_features = ServiceFeatures(dbtype)
        self.helper = RdfHelper()

    def from_space(self, cspace):
        self.gspace = GroundingSpaceRef(cspace)

    def __collect_conditions(self, query_components):
        sparql_query = ""
        for condition in query_components.conditions:
            sparql_query += condition + " . \n"
        for filter in query_components.filters:
            sparql_query += f"filter ({filter})\n"

        if len(query_components.filter_not_exists) > 0:
            sparql_query += "filter not exists {"
            for filter in query_components.filter_not_exists:
                sparql_query += f"{filter} .\n"
            sparql_query += "}"
        return sparql_query

    def construct_query(self, query_atom):
        query_components = self.helper.get_fields_and_conditions(query_atom)
        sparql_query = ""
        for key, prefix in self.service_features.prefixes.items():
            sparql_query += f"PREFIX {key}: {prefix}" + "\n"
        fixed_variables = " ".join([f"?{var}" for var in query_components.variables])

        sparql_query += f"SELECT distinct {fixed_variables}\n" if query_components.distinct else f"SELECT {fixed_variables}\n"
        if self.service_features.service or len(query_components.conditions) > 0 or len(query_components.filters) > 0:
            sparql_query += "WHERE {\n"
            if self.service_features.service:
                sparql_query += f"SERVICE {self.service_features.service}" + "{\n"

            sparql_query += self.__collect_conditions(query_components)

            if len(query_components.union) > 0:
                for union in query_components.union:
                    union_conditions = []
                    for component in union:
                        condition = self.__collect_conditions(component)
                        union_conditions.append(f"{{{condition}}}")
                    if len(union_conditions) > 0:
                        sparql_query += "{" + " UNION ".join(union_conditions) + "}\n"

            if len(query_components.optional) > 0:
                optional_conditions = ""
                for component in query_components.optional:
                    optional_conditions = self.__collect_conditions(component)
                if optional_conditions:
                    sparql_query += f"Optional {{{optional_conditions}}} \n"

            if self.service_features.service:
                sparql_query += "}"
            sparql_query += "}\n"
        if len(query_components.order_asc) > 0:
            sparql_query += f"ORDER BY ASC "
            for order in query_components.order_asc:
                sparql_query += f"({order}) "
        if len(query_components.order_desc) > 0:
            sparql_query += f"ORDER BY DESC "
            for order in query_components.order_desc:
                sparql_query += f"({order}) "
        if query_components.limit:
            sparql_query += f"Limit {query_components.limit} "
        if query_components.offset:
            sparql_query += f"OFFSET {query_components.offset} "


        return sparql_query, query_components.variables

    def query(self, query_atom):
        try:
            new_bindings_set = BindingsSet.empty()
            sparql_query, vars_names = self.construct_query(query_atom)
            if sparql_query:
                graph = Graph()
                values = []
                vars_names = list(vars_names)
                for r in graph.query(sparql_query):
                    row = []
                    for var in vars_names:
                        row.append(r.get(var))
                    values.append(row)
                if len(vars_names) > 0 and len(values) > 0:
                    return results2bindings(vars_names, values)
            return new_bindings_set
        except Exception as error:
            print(error)


@register_atoms
def sql_space_atoms():
    newRDFSpaceAtom = OperationAtom('new-rdf-space', lambda db_type: [
        G(SpaceRef(RdfSpace(db_type)))], unwrap=False)

    return {
        r"new-rdf-space": newRDFSpaceAtom
    }
