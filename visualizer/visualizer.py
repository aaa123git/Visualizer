from bytecode import Bytecode, Instr, FreeVa, CellVar

class get_local(object):
    cache = {}
    is_activate = False

    def __init__(self, varname):
        self.varname = varname

    def __call__(self, func):
        if not type(self).is_activate:
            return func

        type(self).cache[func.__qualname__] = []
        extra_code = []
        if self.varname in func.__code__.co_varnames:
            extra_code.append(Instr("LOAD_FAST", self.varname))
        elif self.varname in func.__code__.co_freevars:
            extra_code.append(Instr("LOAD_DEREF", FreeVar(self.varname)))
        elif self.varname in func.__code__.co_cellvars:
            extra_code.append(Instr("LOAD_DEREF", CellVar(self.varname)))
        else:
            raise NameError(f"local variable {self.varname} is not found. It may be a global variable.")
        extra_code.append(Instr("BUILD_TUPLE", 2))
        c = Bytecode.from_code(func.__code__)
        c.clear()
        for instr in Bytecode.from_code(func.__code__):
            if isinstance(instr, Instr) and instr._name == 'RETURN_VALUE':
                c.extend(extra_code)
            c.append(instr)
        func.__code__ = c.to_code()

        def wrapper(*args, **kwargs):
            res, values = func(*args, **kwargs)
            type(self).cache[func.__qualname__].append(values.detach().cpu().numpy())
            return res
        return wrapper

    @classmethod
    def clear(cls, key=None):
        if key is not None:
            if not isinstance(key, str):
                key = key.__qualname__
            cls.cache.pop(key)
        else:
            cls.cache.clear()

    @classmethod
    def activate(cls):
        cls.is_activate = True
