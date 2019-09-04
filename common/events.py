__all__ = [
    "events"
]

from .lazy import (
    lazy # used by `add_events` during `exec`
)


def events(*_events):
    """ A class decorator. Adds auxiliary methods for callback based event
notification of multiple watchers.
    """

    def add_events(cls):
        # Maintain total event list of both inherited events and events added
        # using nested decorations.
        try:
            all_events = cls.events
        except AttributeError:
            cls.events = _events
        else:
            cls.events = all_events + _events

        for e in _events:
            helpers = {}
            exec("""
@lazy
def {event}_handlers(self):
    return []

def {event}(self, *a, **kw):
    for h in list(self.{handlers}):
        h(*a, **kw)

def watch_{event}(self, cb):
    self.{handlers}.append(cb)

def unwatch_{event}(self, cb):
    self.{handlers}.remove(cb)

""".format(event = e, handlers = e + "_handlers"),
                globals(), helpers
            )

            for n, h in helpers.items():
                setattr(cls, n, h)

        return cls

    return add_events
