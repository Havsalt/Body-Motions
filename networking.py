import subprocess as _subprocess


_IPV4_SEARCH_DELIMITER = ": "
_PORT = 7878


def get_address() -> tuple[str, int]:
    result = _subprocess.run(["ipconfig"], text=True, capture_output=True).stdout
    host = None
    for line in result.splitlines():
        if "IPv4" in line:
            start = line.rindex(_IPV4_SEARCH_DELIMITER) + len(_IPV4_SEARCH_DELIMITER)
            host = line[start:]
    assert isinstance(host, str)
    port = 7878
    return (host, port)
