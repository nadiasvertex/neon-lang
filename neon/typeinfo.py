__author__ = 'Christopher Nelson'


class TypeBase:
    def __init__(self, type_id):
        self.type_id = type_id


class IntType(TypeBase):
    def __init__(self):
        TypeBase.__init__(self, 1)


class StringType(TypeBase):
    def __init__(self):
        TypeBase.__init__(self, 2)


class TypeIdCounter:
    def __init__(self):
        self.type_id_base = 63

    def next(self):
        self.type_id_base += 1
        return self.type_id_base


type_id_base = TypeIdCounter()


class UserDefinedType(TypeBase):
    def __init__(self, type_definition):
        TypeBase.__init__(self, type_id_base.next())

        self.definition = type_definition
        self.members = []
        self.member_names = {}

    def check(self, scope):
        for m in self.definition.members:
            t = scope.get(m.type_name, None)
            if t is None:
                print("Unknown type name '%s' in '%s': '%s %s'" % (
                    m.type_name, self.definition.name, m.alias_name, m.type_name
                ))
                return False

            self.members.append(t)
            self.member_names[m.alias_name] = t

        return True


def new_scope():
    return {
        "Int": IntType(),
        "String": StringType()
    }
