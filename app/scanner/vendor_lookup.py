VENDOR_PREFIXES = {
    "00:1A:A0": "Dell",
    "3C:52:82": "Hewlett Packard",
    "00:80:92": "Zebra Technologies",
    "00:26:AB": "Seiko Epson",
    "FC:EC:DA": "Ubiquiti",
    "D8:47:32": "Cisco",
}


def lookup_vendor(mac_address: str | None) -> str | None:
    if not mac_address:
        return None
    normalized = mac_address.upper().replace("-", ":")
    prefix = ":".join(normalized.split(":")[:3])
    return VENDOR_PREFIXES.get(prefix)
