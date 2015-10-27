from neon import ast

__author__ = 'Christopher Nelson'

TOKEN_KEYWORD = 0
TOKEN_IDENT = 1
TOKEN_TYPE_NAME = 2


class Memo:
    def __init__(self, kind, state, token):
        self.kind = kind
        self.state = state
        self.token = token


class Transaction:
    def __init__(self, cursor):
        self.cursor = cursor
        self.committed = False

    def __enter__(self):
        self.cursor.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.committed:
            self.cursor.rollback()

    def commit(self):
        self.committed = True


class Cursor:
    def __init__(self, filename):
        self.index = 0
        self.line_no = 1
        self.column = 1
        self.filename = filename

        self.stack = []

    def __str__(self):
        return "%s:%d:%d" % (self.filename, self.line_no, self.column)

    def transaction(self):
        return Transaction(self)

    def eof(self, data):
        return self.index >= len(data)

    def begin(self):
        self.stack.append(self.get_state())

    def rollback(self):
        self.put_state(self.stack.pop())

    def commit(self):
        self.stack.pop()

    def get_state(self):
        return self.index, self.line_no, self.column

    def put_state(self, state):
        self.index, self.line_no, self.column = state

    def skip_white_space(self, data):
        while not self.eof(data) and data[self.index].isspace():
            c = data[self.index]
            self.index += 1

            if c == "\n":
                self.column = 1
                self.line_no += 1
            else:
                self.column += 1

    def peek(self, data):
        if self.eof(data):
            return None

        return data[self.index]

    def read(self, data):
        if self.eof(data):
            return None

        c = data[self.index]
        self.index += 1
        self.column += 1
        return c

    def match_indent(self, data):
        # Find the next newline.
        self.begin()
        while True:
            c = self.read(data)
            if c in " \r\t":
                continue

            if c == "\n":
                self.line_no += 1
                self.column = 1
                break

            self.rollback()
            return False, 0

        indent_length = 0
        while True:
            c = self.peek(data)
            if c is None or c not in " \t":
                break

            indent_length += 1
            self.read(data)

        if indent_length == 0:
            self.rollback()
            return False, 0

        self.commit()
        return True, indent_length

    def match_keyword(self, data, keyword):
        self.skip_white_space(data)
        self.begin()
        for c in keyword:
            if c != self.read(data):
                self.rollback()
                return False

        self.commit()
        return True

    def match_pattern(self, data, initial_chars, final_chars):
        self.skip_white_space(data)
        self.begin()
        c = self.read(data)
        if c is None or c not in initial_chars:
            self.rollback()
            return False, None

        token = c
        while True:
            c = self.peek(data)
            if c is None or c not in final_chars:
                self.commit()
                return True, token

            token += self.read(data)


class Parser:
    def __init__(self, types=None):
        self.memo = {}
        self.types = types if types is not None else {}

    def error(self, cursor, msg):
        print("%s %s" % (str(cursor), msg))

    def memoize(self, index, kind, cursor, token):
        self.memo[index] = Memo(kind, cursor.get_state(), token)
        return True, token

    def memoized(self, index, kind, cursor):
        m = self.memo.get(index)
        if m is not None and m.kind == kind:
            cursor.put_state(m.state)
            return True, m.token

        return False, None

    def keyword(self, data, cursor, keyword):
        index = cursor.index
        m = self.memoized(index, TOKEN_KEYWORD, cursor)
        if m[0] and m[1] == keyword: return m

        found = cursor.match_keyword(data, keyword)
        if not found:
            return False, None

        return self.memoize(index, TOKEN_KEYWORD, cursor, keyword)

    def identifier(self, data, cursor):
        index = cursor.index
        m = self.memoized(index, TOKEN_IDENT, cursor)
        if m[0]: return m

        ident_start_chars = "_abcdefghijklmnopqrstuvwxyz"
        ident_final_chars = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        found, token = cursor.match_pattern(data, ident_start_chars, ident_final_chars)
        if not found:
            return False, None

        return self.memoize(index, TOKEN_IDENT, cursor, token)

    def type_name(self, data, cursor):
        index = cursor.index
        m = self.memoized(index, TOKEN_TYPE_NAME, cursor)
        if m[0]: return m

        type_name_start_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        type_name_final_chars = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        found, token = cursor.match_pattern(data, type_name_start_chars, type_name_final_chars)
        if not found:
            return False, None

        return self.memoize(index, TOKEN_TYPE_NAME, cursor, token)

    def type_declaration(self, data, cursor):
        # Match a simple type name
        found, type_name = self.type_name(data, cursor)
        if found:
            return True, ast.TypeName(type_name)

        # Match an array type name
        with cursor.transaction() as txn:
            found, _ = self.keyword(data, cursor, "[")
            if found:
                found, type_name = self.type_name(data, cursor)
                if found:
                    found, _ = self.keyword(data, cursor, "]")
                    if found:
                        txn.commit()
                        return True, ast.TypeName(type_name, is_array=True)
                    else:
                        self.error(cursor, "Expected ']'")
                        return False, None

        # Match a map type name
        found, _ = self.keyword(data, cursor, "{")
        if found:
            found, key_type_name = self.type_name(data, cursor)
            if found:
                found, _ = self.keyword(data, cursor, ":")
                if found:
                    found, value_type_name = self.type_name(data, cursor)
                    if found:
                        found, _ = self.keyword(data, cursor, "}")
                        if found:
                            return True, ast.TypeName(key_type_name, value_name=value_type_name, is_map=True)
                        else:
                            self.error(cursor, "Expected '}'")
                            return False, None

        found, _ = self.keyword(data, cursor, "()")
        if found:
            return True, ast.TypeName("()")

        return False, None

    def function_signature(self, data, cursor):
        def coalesce(v):
            return v if v else None

        with cursor.transaction() as txn:
            found, func_name = self.identifier(data, cursor)
            if not found:
                return False, None

            found, _ = self.keyword(data, cursor, "::")
            if not found:
                return False, None

            inputs = []
            while True:
                found, type_decl = self.type_declaration(data, cursor)
                if found:
                    inputs.append(type_decl)
                    continue

                break

            found, _ = self.keyword(data, cursor, "=")
            if not found:
                txn.commit()
                return True, ast.FunctionSignature(func_name, coalesce(inputs), None)

            outputs = []
            while True:
                found, type_decl = self.type_declaration(data, cursor)
                if found:
                    outputs.append(type_decl)
                    continue

                break

            txn.commit()
            return True, ast.FunctionSignature(func_name, coalesce(inputs), coalesce(outputs))

    def type_definition(self, data, cursor):
        found, _ = self.keyword(data, cursor, "type")
        if not found:
            return False, None

        found, type_name = self.type_name(data, cursor)
        if not found:
            self.error(cursor, "Expected a typename.")
            return False, None

        # Detect simple type alias
        found, alias_of = self.type_name(data, cursor)
        if found:
            return True, ast.TypeAlias(type_name, alias_of)

        # Detect ADT type suite
        found, _ = self.keyword(data, cursor, ":")
        if not found:
            self.error(cursor, "Expected ':'")
            return False, None

        members = []
        indent_length = None
        while True:
            found, length = cursor.match_indent(data)
            if not found:
                break

            if indent_length is None:
                indent_length = length
            elif length > indent_length:
                self.error(cursor, "Unexpected indent.")
                return False, None
            elif length < indent_length:
               break

            found, alias_name = self.type_name(data, cursor)
            if not found:
                break

            found, type_name = self.type_name(data, cursor)
            if not found:
                break

            members.append(ast.AdtMember(alias_name, type_name))

        return (False, None) if len(members) == 0 else (True, ast.AdtTypeDefinition(type_name, members))

    def deconstructor(self, data, cursor):
        found, _ = self.keyword(data, cursor, "(")
        if not found:
            return False, None

        found, type_name = self.type_name(data, cursor)
        if not found:
            return False, None

        bindings = []
        while True:
            found, decon = self.deconstructor(data, cursor)
            if found:
                bindings.append(decon)
                continue

            found, var_name = self.identifier(data, cursor)
            if not found:
                break

            bindings.append(ast.DeconstructorBinding(len(bindings), var_name))

        found, _ = self.keyword(data, cursor, ")")
        if not found:
            self.error(cursor, "Expected ')'")
            return False, None

        return ast.Deconstructor(type_name, bindings)

    def function(self, data, cursor):
        with cursor.transaction() as txn:
            found, func_name = self.identifier(data, cursor)
            if not found:
                return False, None
