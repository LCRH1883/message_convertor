from __future__ import annotations
import datetime

SEP = "=" * 90

def write_record(out, rec: dict):
    out.write(SEP + "\n")
    out.write(f"FILE: {rec.get('file','')}\n")
    out.write(f"SOURCE: {rec.get('source','')}\n")
    out.write(f"DATE: {rec.get('date','')}\n")
    out.write(f"FROM: {rec.get('from','')}\n")
    out.write(f"TO: {rec.get('to','')}\n")
    out.write(f"SUBJECT: {rec.get('subject','')}\n")
    if rec.get("message_id"):
        out.write(f"MESSAGE-ID: {rec.get('message_id')}\n")
    out.write("\n")
    out.write(rec.get("body", "") + "\n")
    out.write(SEP + "\n\n")

def write_header(out, source_root: str):
    header = (
        f"# Combined MSG/EML/PST Export\n"
        f"# Created: {datetime.datetime.now().isoformat()}\n"
        f"# Source: {source_root}\n\n"
    )
    out.write(header)