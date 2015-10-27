__author__ = 'Christopher Nelson'


class TypeName:
    def __init__(self, name, is_array=False, is_map=False, value_name=None):
        self.name = name
        self.is_array = is_array
        self.is_map = is_map
        if is_map:
            self.key_name = name
            self.value_name = value_name
        else:
            self.key_name = None
            self.value_name = None


class FunctionSignature:
    def __init__(self, name, inputs, outputs):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs


class TypeAlias:
    def __init__(self, alias_name, type_name):
        self.alias_name = alias_name
        self.type_name = type_name


class AdtTypeDefinition:
    def __init__(self, name, members):
        self.name = name
        self.members = members


class AdtMember:
    def __init__(self, alias_name, type_name):
        self.alias_name = alias_name
        self.type_name = type_name


class DeconstructorBinding:
    def __init__(self, index, var_name):
        self.index = index
        self.var_name = var_name


class Deconstructor:
    def __init__(self, type_name, bindings):
        self.type_name = type_name
        self.bindings = bindings
