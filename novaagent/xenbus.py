
from pyxs.exceptions import UnexpectedPacket
from pyxs.client import Router


from pyxs._internal import Event
from pyxs._internal import NUL
from pyxs._internal import Op


import select


class XenGuestRouter(Router):
    def __call__(self):
        try:
            while True:
                rlist, _wlist, _xlist = select.select(
                    [self.connection, self.r_terminator], [], [])
                if not rlist:
                    continue
                elif self.r_terminator in rlist:
                    break

                packet = self.connection.recv()
                if packet.op == Op.WATCH_EVENT:
                    event = Event(*packet.payload.split(NUL)[:-1])
                    for monitor in self.monitors[event.token]:
                        monitor.events.put(event)
                else:
                    """
                        The try/except is the reason for the subclass from the
                        pyxs package. Since this is on the guest only the below
                        gets the packet payload and returns it without the
                        validation piece failing.
                    """
                    rvar = None
                    try:
                        self.rvars[packet.rq_id]
                        rvar = self.rvars.pop(packet.rq_id, None)
                    except Exception:
                        temp_rq_id = list(self.rvars.keys())[0]
                        rvar = self.rvars.pop(temp_rq_id, None)

                    if rvar is None:
                        raise UnexpectedPacket(packet)
                    else:
                        rvar.set(packet)
        finally:
            self.connection.close()
            self.r_terminator.close()
            self.w_terminator.close()
