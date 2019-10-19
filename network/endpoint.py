__all__ = [
    "Endpoint"
]

from .protocol import (
    LENGTH
)
from six.moves.cPickle import (
    loads,
    dumps
)


class Endpoint(object):

    @property
    def socket(self):
        return self._socket

    @socket.setter
    def socket(self, socket):
        recv, send = socket.recv, socket.send
        pack, unpack = LENGTH.pack, LENGTH.unpack

        def handle_message(chunk):
            length = b""
            while len(length) < 4:
                if len(chunk) == 0:
                    chunk = recv(1024)
                    if not chunk:
                        return None
                length += chunk
                chunk = b""

            msg_len = unpack(length[:4])[0]
            data = length[4:]

            while len(data) < msg_len:
                chunk = recv(1024)
                if not chunk:
                    return None
                data += chunk

            if len(data) > msg_len:
                chunk = data[msg_len:]
                data = data[:msg_len]
            else:
                chunk = b""

            msg_name, arg = loads(data)

            getattr(self, "_msg_" + msg_name)(arg)

            return chunk

        self.handle_message = handle_message

        def send_message(name, arg):
            msg = (name, arg)
            data = dumps(msg)
            length = pack(len(data))
            frame = length + data

            while len(frame):
                sent = send(frame)
                if sent == 0:
                    return False
                frame = frame[sent:]

            return True

        self.send_message = send_message

        self._socket = socket
