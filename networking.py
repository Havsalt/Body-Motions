import subprocess as _subprocess


_IPV4_SEARCH_DELIMITER = ": "
_PORT = 7878


def get_address(localhost: bool = True) -> tuple[str, int]:
    if localhost:
        return ("localhost", _PORT)
    result = _subprocess.run(["ipconfig"], text=True, capture_output=True).stdout
    host = None
    for line in result.splitlines():
        if "IPv4" in line:
            start = line.rindex(_IPV4_SEARCH_DELIMITER) + len(_IPV4_SEARCH_DELIMITER)
            host = line[start:]
    assert isinstance(host, str)
    return (host, _PORT)
