

def get_hostname(use_bytes=True):
    if use_bytes:
        return (b'test-server\n', b'')
    else:
        return 'test-server'


def get_xen_host_events():
    return (
        b"""
748dee41-c47f-4ec7-b2cd-037e51da4031 = "{"name": "keyinit"\n""",
        b''
    )


def get_xen_guest_events():
    return (
        b"""cd4ae803-1577-4e37-90b3-3de01bc4bba9 = "{"message": "1.39.1"}"\n
78b3c098-46b3-4a54-b2ff-d2ac15651716 = "{"message": "kmsactivate"}"\n
bb966d88-e06c-499f-b19b-60c06c9e257a = "{"returncode": "0"}"\n""",
        b''
    )


def get_xen_host_event_details():
    return (
        b'{"name": "keyinit", "value": "68436575764933852815830951574296"}\n',
        b''
    )


def get_mac_addresses():
    return (
        b"""
BC764E206C5B = "{"label": "private", "broadcast": "10.208.255.255", "ips": [\\..."\n
BC764E206C5A = "{"ip6s": [{"ip": "2001:4802:7802:104:be76:4eff:fe20:6c5a", "\\..."\n""",  # noqa
        b''
    )


def get_network_interface():
    return (
        b"""
{"label": "private", "broadcast": "10.208.255.255", "ips": [
{"ip": "10.208.227.239", "netmask": "255.255.224.0", "enabled": "1",
"gateway": null}], "mac": "BC:76:4E:20:6C:5B", "routes": [
{"route": "10.208.0.0", "netmask": "255.240.0.0", "gateway": "10.208.224.1"},
{"route": "10.176.0.0", "netmask": "255.240.0.0", "gateway": "10.208.224.1"}],
"gateway": null}\n""",
        b''
    )
