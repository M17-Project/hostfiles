#!/usr/bin/env python3
"""Build M17Hosts.txt and M17Hosts.json from DVRef API responses.

Usage: build_hostfiles.py <input_dir> <output_dir>

<input_dir> must contain:
  mrefd.json     GET /api/v2/mrefd/reflectors/
  urfd.json      GET /api/v2/urfd/reflectors/
  vex_*.json     GET /api/v2/vex/servers/<slug>/   (one per server; may be none)

Output files are rewritten only when something other than the generation
timestamp changed, so unchanged data produces no git diff.
"""

import glob
import json
import os
import sys
from datetime import datetime, timezone

ATTRIBUTION = "Reflector data provided by DVRef — https://dvref.com/"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
SOURCE_URL = "https://github.com/M17-Project/hostfiles"
URFD_M17_PORT = 17000  # DVRef does not publish the URFD M17 port; 17000 is the default.


def load(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    if doc.get("status") != "success":
        sys.exit(f"{path}: status is {doc.get('status')!r}, expected 'success'")
    return doc["data"]


def mrefd_entries(data):
    out = []
    for r in data["reflectors"]:
        e = dict(r)
        e["designator"] = "M17-" + r["designator"]
        e["source"] = "mrefd"
        out.append(e)
    return out


def urfd_entries(data):
    out = []
    for r in data["reflectors"]:
        if "M17" not in (r.get("enabled_modes") or []):
            continue
        e = dict(r)
        e["designator"] = "URF" + r["designator"]
        e["port"] = URFD_M17_PORT
        e["source"] = "urfd"
        out.append(e)
    return out


def vex_entries(servers):
    out = []
    for s in servers:
        for i in s.get("instances", []):
            if i.get("mode") != "M17" or not i.get("is_listed", True):
                continue
            d = i["designator"]
            out.append({
                "designator": "VEX" + (d[3:] if d.upper().startswith("VEX") else d),
                "name": i.get("name") or s.get("name"),
                "slug": i.get("slug"),
                "url": s.get("url"),
                "dns": i.get("effective_dns") or i.get("dns"),
                "ipv4": i.get("effective_ipv4") or i.get("ipv4") or i.get("cached_ipv4"),
                "ipv6": i.get("effective_ipv6") or i.get("ipv6") or i.get("cached_ipv6"),
                "modules": i.get("m17_modules") or [],
                "port": i.get("port"),
                "sponsor": s.get("sponsor"),
                "country": s.get("country"),
                "dns_cache_updated_at": i.get("dns_cache_updated_at"),
                "last_verified_at": s.get("last_verified_at"),
                "source": "vex",
            })
    return out


def endpoint(e):
    return (e.get("ipv4") or e.get("ipv6"), e.get("port"))


def write_if_changed(path, content, strip):
    """Write content unless it matches the existing file apart from lines/keys `strip` removes."""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
        if strip(old) == strip(content):
            print(f"{os.path.basename(path)}: unchanged")
            return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{os.path.basename(path)}: written")


def main(indir, outdir):
    mrefd = mrefd_entries(load(os.path.join(indir, "mrefd.json")))
    urfd = urfd_entries(load(os.path.join(indir, "urfd.json")))
    vex_servers = [load(p)["server"] for p in sorted(glob.glob(os.path.join(indir, "vex_*.json")))]
    vex = vex_entries(vex_servers)

    if not mrefd:
        sys.exit("No MREFD reflectors returned; refusing to publish an empty list.")

    # VEX instances that duplicate an existing reflector's ip:port are skipped.
    seen = {endpoint(e) for e in mrefd + urfd}
    vex = [e for e in vex if endpoint(e) not in seen]

    entries = sorted(mrefd + urfd + vex, key=lambda e: e["designator"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # --- JSON ---
    doc = {
        "_metadata": {
            "filename": "M17Hosts.json",
            "generated": now,
            "source_url": SOURCE_URL,
            "attribution": ATTRIBUTION,
            "license": LICENSE_URL,
            "modified": "Combined from DVRef MREFD, URFD (M17-enabled) and VEX (M17 instances); designators prefixed.",
        },
        "reflectors": entries,
    }
    json_text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"

    def json_strip(text):
        try:
            d = json.loads(text)
        except ValueError:
            return text
        d.get("_metadata", {}).pop("generated", None)
        return d

    write_if_changed(os.path.join(outdir, "M17Hosts.json"), json_text, json_strip)

    # --- TXT ---
    lines = [
        "#",
        "# M17Hosts.txt",
        "#",
        f"# Generated: {now}",
        f"# Source:    {SOURCE_URL}",
        "#",
        f"# {ATTRIBUTION}",
        f"# Licensed CC BY 4.0 ({LICENSE_URL}).",
        "# Modified: combined from DVRef MREFD, URFD and VEX listings and reformatted.",
        "#",
    ]
    skipped = []
    for e in entries:
        ip = e.get("ipv4") or e.get("ipv6")
        if not ip or not e.get("port"):
            skipped.append(e["designator"])
            continue
        lines.append(f"{e['designator']} {ip} {e['port']}")
    txt = "\n".join(lines) + "\n"

    def txt_strip(text):
        return [l for l in text.splitlines() if not l.startswith("# Generated:")]

    write_if_changed(os.path.join(outdir, "M17Hosts.txt"), txt, txt_strip)

    print(f"{len(mrefd)} MREFD, {len(urfd)} URFD, {len(vex)} VEX -> {len(entries)} entries")
    if skipped:
        print("No address/port, omitted from txt: " + " ".join(skipped))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
