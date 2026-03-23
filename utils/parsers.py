"""
utils/parsers.py — Parse ADB output into structured data
"""

import re
from dataclasses import dataclass, field


@dataclass
class ContentRow:
    index: int
    data: dict = field(default_factory=dict)

    def __str__(self):
        parts = ", ".join(f"{k}={v}" for k, v in self.data.items())
        return f"Row {self.index}: {parts}"


def parse_content_rows(output: str) -> list[ContentRow]:
    rows = []
    row_re = re.compile(r'^Row:\s*(\d+)\s+(.*)', re.MULTILINE)
    for m in row_re.finditer(output):
        idx = int(m.group(1))
        raw = m.group(2).strip()
        data = {}
        parts = re.split(r',\s*(?=[a-zA-Z_][a-zA-Z0-9_]*=)', raw)
        for part in parts:
            if "=" in part:
                k, _, v = part.partition("=")
                data[k.strip()] = v.strip()
        rows.append(ContentRow(index=idx, data=data))
    return rows


def extract_columns(rows: list[ContentRow]) -> list[str]:
    seen = {}
    for row in rows:
        for col in row.data:
            if col not in seen:
                seen[col] = None
    return list(seen.keys())


def extract_content_uris(dumpsys_output: str) -> list[dict]:
    uris = []
    seen = set()
    authority_re  = re.compile(r'authority[=:\s]+([^\s;,]+)', re.IGNORECASE)
    uri_re        = re.compile(r'content://[^\s"\'<>\)]+', re.IGNORECASE)
    exported_re   = re.compile(r'exported=(\w+)', re.IGNORECASE)
    permission_re = re.compile(r'(?:read|write)Permission[=:\s]+([^\s;,\)]+)', re.IGNORECASE)
    lines = dumpsys_output.splitlines()
    for i, line in enumerate(lines):
        for m in authority_re.finditer(line):
            auth = m.group(1).rstrip(";,\"'")
            uri = f"content://{auth}"
            if uri not in seen:
                seen.add(uri)
                context = "\n".join(lines[max(0, i-5):i+5])
                em = exported_re.search(context)
                pm = permission_re.search(context)
                uris.append({
                    "uri":        uri,
                    "authority":  auth,
                    "exported":   em.group(1) if em else "unknown",
                    "permission": pm.group(1) if pm else "",
                })
        for m in uri_re.finditer(line):
            uri = m.group(0).rstrip(";,\"')")
            if uri not in seen:
                seen.add(uri)
                uris.append({
                    "uri":        uri,
                    "authority":  uri.replace("content://", "").split("/")[0],
                    "exported":   "unknown",
                    "permission": "",
                })
    return uris


def sdk_to_android_name(sdk: str) -> str:
    mapping = {
        "21": "5.0 Lollipop",    "22": "5.1 Lollipop MR1",
        "23": "6.0 Marshmallow", "24": "7.0 Nougat",
        "25": "7.1 Nougat MR1",  "26": "8.0 Oreo",
        "27": "8.1 Oreo MR1",    "28": "9 Pie",
        "29": "10 (Q)",           "30": "11 (R)",
        "31": "12 (S)",           "32": "12L (S_V2)",
        "33": "13 (T)",           "34": "14 (U)",
        "35": "15 (V)",           "36": "16 (Baklava)",
    }
    return mapping.get(sdk.strip(), f"SDK {sdk}")


def abi_to_description(abi: str) -> str:
    mapping = {
        "arm64-v8a":  "ARM 64-bit (arm64-v8a)  — modern flagship",
        "armeabi-v7a":"ARM 32-bit (armeabi-v7a) — legacy/older device",
        "x86_64":     "x86 64-bit              — emulator / Intel tablet",
        "x86":        "x86 32-bit              — emulator / older Intel",
    }
    return mapping.get(abi.strip(), abi)


# ── Permission Parser ─────────────────────────────────────────────────────────
DANGEROUS_PERMS = {
    "READ_CONTACTS", "WRITE_CONTACTS", "READ_CALL_LOG", "WRITE_CALL_LOG",
    "READ_PHONE_STATE", "READ_PHONE_NUMBERS", "CALL_PHONE", "ADD_VOICEMAIL",
    "USE_SIP", "PROCESS_OUTGOING_CALLS", "READ_CALENDAR", "WRITE_CALENDAR",
    "CAMERA", "RECORD_AUDIO", "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE",
    "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION", "ACCESS_BACKGROUND_LOCATION",
    "READ_SMS", "SEND_SMS", "RECEIVE_SMS", "RECEIVE_WAP_PUSH", "RECEIVE_MMS",
    "BODY_SENSORS", "ACTIVITY_RECOGNITION", "BLUETOOTH_SCAN", "BLUETOOTH_CONNECT",
    "BLUETOOTH_ADVERTISE", "MANAGE_EXTERNAL_STORAGE", "GET_ACCOUNTS",
    "USE_BIOMETRIC", "USE_FINGERPRINT", "ANSWER_PHONE_CALLS",
}


def parse_permissions(dumpsys_output: str) -> dict:
    """
    Parse dumpsys package output for granted/denied permissions.
    Returns: {"dangerous": [...], "normal": [...]}
    Each item: {"name": str, "granted": bool}
    """
    dangerous = []
    normal    = []

    # Match lines like: android.permission.CAMERA: granted=true
    perm_re = re.compile(
        r'(android\.permission\.\w+|com\.\w+\.permission\.\w+)'
        r'.*?granted=(\w+)',
        re.IGNORECASE,
    )
    # Also match simple granted permission lists
    granted_re = re.compile(r'android\.permission\.(\w+)', re.IGNORECASE)

    seen = set()
    for line in dumpsys_output.splitlines():
        m = perm_re.search(line)
        if m:
            full_name = m.group(1)
            granted   = m.group(2).lower() == "true"
            short     = full_name.split(".")[-1].upper()
            if full_name not in seen:
                seen.add(full_name)
                entry = {"name": full_name, "granted": granted}
                if short in DANGEROUS_PERMS:
                    dangerous.append(entry)
                else:
                    normal.append(entry)
        else:
            # Look for permission names in install section
            for m2 in granted_re.finditer(line):
                full_name = f"android.permission.{m2.group(1)}"
                if full_name not in seen and "permission" in line.lower():
                    seen.add(full_name)
                    short = m2.group(1).upper()
                    entry = {"name": full_name, "granted": False}
                    if short in DANGEROUS_PERMS:
                        dangerous.append(entry)

    return {"dangerous": dangerous, "normal": normal}


# ── Exported Component Parser ─────────────────────────────────────────────────
def parse_exported_components(dumpsys_output: str, package: str) -> dict:
    """
    Parse dumpsys package output for exported Activities, Services, Receivers, Providers.
    Returns dict: {"Activities": [...], "Services": [...], "Receivers": [...], "Providers": [...]}
    """
    result = {"Activities": [], "Services": [], "Receivers": [], "Providers": []}

    # Pattern: <package>/<class> followed (within a few lines) by exported=true
    comp_re = re.compile(
        rf'({re.escape(package)}/[\w.$]+)',
        re.IGNORECASE,
    )
    exported_re = re.compile(r'exported=true', re.IGNORECASE)

    # Section markers
    section_map = {
        "Activity Resolver Table":   "Activities",
        "Receiver Resolver Table":   "Receivers",
        "Service Resolver Table":    "Services",
        "Provider":                  "Providers",
        "Activities:":               "Activities",
        "Services:":                 "Services",
        "Receivers:":                "Receivers",
        "ContentProviders:":         "Providers",
    }

    lines = dumpsys_output.splitlines()
    current_section = None

    for i, line in enumerate(lines):
        # Detect section
        for marker, kind in section_map.items():
            if marker in line:
                current_section = kind
                break

        # Look for exported components
        m = comp_re.search(line)
        if m:
            comp = m.group(1)
            # Check nearby lines for exported=true
            context = "\n".join(lines[i:min(i+8, len(lines))])
            if exported_re.search(context):
                target = current_section or "Activities"
                short_comp = comp.split("/")[1] if "/" in comp else comp
                if short_comp not in result[target]:
                    result[target].append(short_comp)

    return result
