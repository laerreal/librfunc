# A test for common.events

from librfunc import (
    events
)

@events("a")
@events("c", "d")
class C(object):

    def gen(self):
        self.a("1")
        self.b(v = "2")

@events("b")
class D(C):
    pass

def handler(*a, **kw):
    print(a, kw)

d = D()
d.watch_a(handler)
d.watch_b(handler)
d.gen()
d.unwatch_a(handler)
d.unwatch_b(handler)
d.gen()

print(d.events)

c = C()
print(c.events)
