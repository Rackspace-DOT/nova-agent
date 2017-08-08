
from subprocess import PIPE
from subprocess import Popen


import json


def xenstore_read(path, client, to_json=False):
    result = None
    if client is None:
        p = Popen(
            ['xenstore-read', path],
            stdout=PIPE,
            stderr=PIPE
        )
        output, _ = p.communicate()
        if p.returncode == 0:
            result = output.decode('utf-8').strip()
    else:
        result = client.read(path).decode('utf-8').strip()

    if result and to_json:
        return json.loads(result)

    return result


def xenstore_list(path, client):
    result = []
    if client is None:
        p = Popen(
            ['xenstore-ls', path],
            stdout=PIPE,
            stderr=PIPE
        )
        out, _ = p.communicate()
        if p.returncode == 0:
            decoded_out = out.decode('utf-8').split('\n')
            result = [
                item.split(' = ')[0] for item in decoded_out if item
            ]
    else:
        for item in client.list(path):
            result.append(item.decode('utf-8').strip())

    return result


def xenstore_write(write_path, write_value, client):
    if client is None:
        p = Popen(
            ['xenstore-write', write_path, write_value],
            stdout=PIPE,
            stderr=PIPE
        )
        p.communicate()
        if p.returncode != 0:
            raise ValueError(
                'Shell to xenstore-write returned invalid code {0}'.format(
                    p.returncode
                )
            )
    else:
        client.write(write_path, write_value)

    return


def xenstore_delete(path, client):
    if client is None:
        p = Popen(
            ['xenstore-rm', path],
            stdout=PIPE,
            stderr=PIPE
        )
        _out, _err = p.communicate()
        if p.returncode != 0:
            raise ValueError(
                'Shell to xenstore-rm returned invalid code {0}'.format(
                    p.returncode
                )
            )

    else:
        client.delete(path)

    return
