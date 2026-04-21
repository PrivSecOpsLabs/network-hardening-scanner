import nmap

def scan_host(target: str, port_range: str = "1-1024") -> dict:
    if not target or not target.strip():
        raise ValueError("Target must be a non-empty string.")
    nm = nmap.PortScanner()
    try:
        nm.scan(hosts=target, ports=port_range, arguments="-sV")
    except nmap.PortScannerError as e:
        error_msg = str(e).lower()
        if "nmap programme was not found" in error_msg or "not found" in error_msg:
            raise NmapNotInstalledError(
                "Nmap is not installed or not in PATH."
                "Install it with: apt install nmap"
            ) from e
        if "permission" in error_msg or "root" in error_msg:
            raise NmapPermissionError(
                "This scan requires elevated privileges. "
                "Try running with sudo."
            ) from e
        raise
    # Host unreachable or down
    if target not in nm.all_hosts():
        return {}
    results = {}

    for proto in nm[target].all_protocols():
        for port in nm[target][proto]:
            port_data = nm[target][proto][port]
            results[str(port)] = {
                "state": port_data.get("state", "unknown"),
                "service": port_data.get("name", ""),
                "version": (
                    f"{port_data.get('product', '')} "
                    f"{port_data.get('version', '')}".strip()
                ),
            }
    return results

class NmapNotInstalledError(RuntimeError):
    """Raised when the Nmap binary cannot be found."""


class NmapPermissionError(PermissionError):
    """Raised when the scan requires privileges the process does not have."""
