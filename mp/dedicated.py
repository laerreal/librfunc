__all__ = [
    "dedicated"
]


from multiprocessing import (
    Process,
    Queue
)


RESERCED = set(["terminate", "fork"])


def dedicated(entity):
    """ Decorator for `pickle`-able class & its methods. A user calls `fork`
on an instance of a decorated class which creates a process with copy of the
instance. Then user calls a `dedicated` method on instance and it will be
actually executed in forked process and return value is fed back.
Both arguments and return value must be `pickle`-able.
Non-decorated methods are executed in context of calling process.
Operation is synchronous. A use case is to launch threads after `fork` using
`dedicated` methods, and the `dedicated` class has role of a thread manager.
    """
    if isinstance(entity, type):
        backends = ["terminate"]
        for name, method in entity.__dict__.items():
            if name in RESERCED:
                raise TypeError(("`%s` attribute name is reserved for " +
                    "`dedicated` implementation") % name
                )
            if not hasattr(method, "_dedicated"):
                continue
            del method._dedicated
            backends.append(name)

        def fork(self):
            c2s, s2c = Queue(1), Queue(1)

            p = Process(target = executor, args = (self, c2s, s2c))
            p.start()

            for name in backends:
                setattr(self, name, gen_frontend(name, c2s, s2c))

        entity.fork = fork
    else: # it's a method in class
        entity._dedicated = True

    return entity


def gen_frontend(name, c2s, s2c):

    def frontend(*a, **kw):
        c2s.put((name, a, kw))
        return s2c.get()

    return frontend


def executor(target, c2s, s2c):

    while True:
        name, a, kw = c2s.get()
        if name == "terminate":
            s2c.put(None)
            break
        s2c.put(getattr(target, name)(*a, **kw))
