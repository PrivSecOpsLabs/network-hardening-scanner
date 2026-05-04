import re
import shutil
import subprocess

def enumerate_local_services() -> list[dict]:
    # try using ss, uses netstat if not available, runtimeError if neither is available
    if shutil.which("ss"):
        raw_output = _run_ss()
        return _parse_ss(raw_output)
    if shutil.which("netstat"):
        raw_output = _run_netstat()
        return _parse_netstat(raw_output)
    raise RuntimeError(
        "Neither 'ss' nor 'netstat' is available on this system. "
        "Install one with: apt install iproute2"
    )

# private helpers
def _run_ss() -> str:
    # run ss -tlnp and return raw stdout
    result = subprocess.run(
        ["ss", "-tlnp"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout

def _run_netstat() -> str:
    # run netstat -tlnp and return raw stdout
    result = subprocess.run(
        ["netstat", "-tlnp"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout

def _parse_ss(output: str) -> list[dict]:
    # parse output from ss into structured records.
    services = []

    for line in output.splitlines():
        # Only process listening lines
        if not line.startswith("LISTEN"):
            continue

        parts = line.split()
        if len(parts) < 5:
            continue

        local_address = parts[3]
        addr, port = _split_address(local_address)
        if port is None:
            continue

        process = _extract_process_ss(line)

        services.append({
            "port":    port,
            "proto":   "tcp",
            "addr":    addr,
            "process": process,
        })

    return services

def _parse_netstat(output: str) -> list[dict]:
    # parse output from netstat -tlnp into structured records
    services = []

    for line in output.splitlines():
        parts = line.split()

        # lines we care about are tcp lines in listen state
        if len(parts) < 7:
            continue
        if parts[0] not in ("tcp", "tcp6"):
            continue
        if parts[5] != "LISTEN":
            continue

        local_address = parts[3]  # ip:port
        addr, port = _split_address(local_address)
        if port is None:
            continue

        process = ""
        if len(parts) >= 7 and "/" in parts[6]:
            process = parts[6].split("/", 1)[1]

        services.append({
            "port":    port,
            "proto":   "tcp",
            "addr":    addr,
            "process": process,
        })

    return services

def _split_address(address: str) -> tuple[str, int | None]:
    # splits addr:port string into components
    # returns tuple of addr_str, port_int or None if it fails

    # ipv6
    ipv6_match = re.match(r"^\[(.+)\]:(\d+)$", address)
    if ipv6_match:
        return ipv6_match.group(1), int(ipv6_match.group(2))

    # ipv4
    if ":" in address:
        addr, _, port_str = address.rpartition(":")
        try:
            return addr, int(port_str)
        except ValueError:
            return address, None

    return address, None

def _extract_process_ss(line: str) -> str:
    # extract the process name from ss output
    # example: users:(("sshd", pid=1234, fd=3))
    match = re.search(r'users:\(\("([^"]+)"', line)
    if match:
        return match.group(1)
    return ""
