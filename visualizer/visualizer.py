from bytecode import Bytecode, Instr, FreeVar

class get_local(object):
    cache = {}
    is_activate = False

    def __init__(self, varname):
        self.varname = varname

    def __call__(self, func):
        if not type(self).is_activate:
            return func

        type(self).cache[func.__qualname__] = []
        c = Bytecode.from_code(func.__code__)
        extra_code = []
        if self.varname in func.__code__.co_varnames:
            extra_code.append(Instr("LOAD_FAST", self.varname))
        elif self.varname in func.__code__.co_freevars:
            extra_code.append(Instr("LOAD_DEREF", FreeVar(self.varname)))
        else:
            raise NameError(f"{self.varname} not found.")
        extra_code.append(Instr("BUILD_TUPLE", 2))
        c[-1:-1] = extra_code
        func.__code__ = c.to_code()

        def wrapper(*args, **kwargs):
            res, values = func(*args, **kwargs)
            type(self).cache[func.__qualname__].append(values.detach().cpu().numpy())
            return res
        return wrapper

    @classmethod
    def clear(cls):
        for key in cls.cache.keys():
            cls.cache[key] = []

    @classmethod
    def activate(cls):
        cls.is_activate = True
