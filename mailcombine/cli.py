from __future__ import annotations
import argparse, traceback, json, csv
from pathlib import Path
from typing import List, Dict, Any, Optional

from mailcombine.writer import write_record, write_header
from mailcombine.extractors import has_embedded_readpst
from mailcore import load_single_message, load_mailbox
from mailcore.legacy import message_to_record

def _progress_emit(progress_path: Optional[Path], payload: dict) -> None:
    if not progress_path: return
    try:
        with open(progress_path, "a", encoding="utf-8") as pf:
            pf.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass

def main(argv=None):
    parser = argparse.ArgumentParser(description="Combine .msg, .eml, and .pst emails into a single searchable .txt file.")
    parser.add_argument("-i", "--input", default="msg_files", help="Root folder to search recursively")
    parser.add_argument("-o", "--output", default="combined_emails.txt", help="Output text file")
    parser.add_argument("--encoding", default="utf-8", help="Output encoding (default utf-8)")
    parser.add_argument("--attachments", action="store_true", help="Also list attachments in the text output")
    parser.add_argument("--json", dest="json_path", default=None, help="Write JSON sidecar log (default: <output>.json)")
    parser.add_argument("--no-json", dest="no_json", action="store_true", help="Disable JSON sidecar logging")
    parser.add_argument("--hashes", action="store_true", help="Write hashes CSV (default: <output>_hashes.csv)")
    parser.add_argument("--hashes-path", dest="hashes_path", default=None, help="Custom path for hashes CSV")
    parser.add_argument("--progress-file", dest="progress_file", default=None, help="Write JSONL progress updates")
    args = parser.parse_args(argv)

    input_path = Path(args.input).expanduser().resolve()
    out_path = Path(args.output).expanduser().resolve()
    json_path = None if args.no_json else (Path(args.json_path).expanduser().resolve() if args.json_path else Path(str(out_path) + ".json"))

    hashes_enabled = bool(args.hashes or args.hashes_path)
    hashes_path: Optional[Path] = None
    if hashes_enabled:
        hashes_path = Path(args.hashes_path).expanduser().resolve() if args.hashes_path else Path(str(out_path).rsplit(".", 1)[0] + "_hashes.csv")

    progress_path: Optional[Path] = Path(args.progress_file).expanduser().resolve() if args.progress_file else None

    if not input_path.exists():
        print(f"[ERROR] Input path does not exist: {input_path}")
        return 2

    base_label = input_path
    msg_files: List[Path]
    eml_files: List[Path]
    pst_files: List[Path]

    if input_path.is_dir():
        msg_files = []
        eml_files = []
        pst_files = []
        for candidate in input_path.rglob("*"):
            if not candidate.is_file():
                continue
            suffix = candidate.suffix.lower()
            if suffix == ".msg":
                msg_files.append(candidate)
            elif suffix == ".eml":
                eml_files.append(candidate)
            elif suffix == ".pst":
                pst_files.append(candidate)
        msg_files.sort()
        eml_files.sort()
        pst_files.sort()
    elif input_path.is_file():
        base_label = input_path.parent
        suffix = input_path.suffix.lower()
        if suffix == ".msg":
            msg_files = [input_path]
            eml_files = []
            pst_files = []
        elif suffix == ".eml":
            msg_files = []
            eml_files = [input_path]
            pst_files = []
        elif suffix == ".pst":
            msg_files = []
            eml_files = []
            pst_files = [input_path]
        else:
            print(f"[ERROR] Unsupported input file type: {input_path.suffix}")
            return 2
    else:
        print(f"[ERROR] Input path is neither file nor directory: {input_path}")
        return 2

    print(f"[INFO] Input source: {input_path}")
    print(f"[INFO] Output file : {out_path}")
    if json_path and not args.no_json: print(f"[INFO] JSON log    : {json_path}")
    if hashes_enabled and hashes_path: print(f"[INFO] Hashes CSV  : {hashes_path}")
    print(f"[INFO] Found {len(msg_files)} .msg, {len(eml_files)} .eml, {len(pst_files)} .pst")

    if progress_path and progress_path.exists():
        try: progress_path.unlink()
        except Exception: pass
    _progress_emit(progress_path, {"phase": "scan", "msg": len(msg_files), "eml": len(eml_files), "pst": len(pst_files)})

    processed = 0
    errors = 0
    json_records: List[Dict[str, Any]] = []
    hash_rows: List[List[str]] = []  # type,parent_source,filename,size,sha256

    def _add_hash_row(row_type: str, parent_source: str, filename: str, size: Any, sha256: Optional[str]):
        if not hashes_enabled: return
        hash_rows.append([row_type, parent_source, filename, str(size if size is not None else ""), sha256 or ""])

    with open(out_path, "w", encoding=args.encoding, errors="replace") as out:
        write_header(out, str(base_label))

        # .msg
        for idx, p in enumerate(msg_files, 1):
            print(f"[INFO] (.msg {idx}/{len(msg_files)}) {p}")
            try:
                message = load_single_message(p)
                rec = message_to_record(message)
                write_record(out, rec, show_attachments=args.attachments)
                json_records.append(rec)
                processed += 1
                _progress_emit(progress_path, {"phase": "processed", "kind": "msg", "file": rec["source"], "processed": processed})
                _add_hash_row("message", rec["source"], rec["file"], None, rec.get("source_sha256"))
                for a in rec.get("attachments", []) or []:
                    _add_hash_row("attachment", rec["source"], a.get("filename",""), a.get("size"), a.get("sha256"))
            except Exception:
                errors += 1
                out.write("="*90 + "\n")
                out.write(f"ERROR reading {p} (.msg):\n")
                out.write(traceback.format_exc())
                out.write("="*90 + "\n\n")
                print(f"[ERROR] Failed .msg: {p}")

        # .eml
        for idx, p in enumerate(eml_files, 1):
            print(f"[INFO] (.eml {idx}/{len(eml_files)}) {p}")
            try:
                message = load_single_message(p)
                rec = message_to_record(message)
                write_record(out, rec, show_attachments=args.attachments)
                json_records.append(rec)
                processed += 1
                _progress_emit(progress_path, {"phase": "processed", "kind": "eml", "file": rec["source"], "processed": processed})
                _add_hash_row("message", rec["source"], rec["file"], None, rec.get("source_sha256"))
                for a in rec.get("attachments", []) or []:
                    _add_hash_row("attachment", rec["source"], a.get("filename",""), a.get("size"), a.get("sha256"))
            except Exception:
                errors += 1
                out.write("="*90 + "\n")
                out.write(f"ERROR reading {p} (.eml):\n")
                out.write(traceback.format_exc())
                out.write("="*90 + "\n\n")
                print(f"[ERROR] Failed .eml: {p}")

        # .pst
        if pst_files:
            if not has_embedded_readpst():
                print("[WARN] PST files present but embedded readpst is not available in this build. Skipping PST.")
                _progress_emit(progress_path, {"phase": "pst_skipped"})
            else:
                _progress_emit(progress_path, {"phase": "pst_start"})
                for idx, pst in enumerate(pst_files, 1):
                    print(f"[INFO] (.pst {idx}/{len(pst_files)}) {pst}")
                    try:
                        mailbox = load_mailbox(pst)
                        extracted_messages = mailbox.all_messages()
                        _progress_emit(progress_path, {"phase": "pst_extracted", "pst": str(pst), "count": len(extracted_messages)})
                        print(f"[INFO]   Extracted {len(extracted_messages)} message(s) from {pst.name}")
                        for eidx, message in enumerate(extracted_messages, 1):
                            try:
                                rec = message_to_record(message)
                                write_record(out, rec, show_attachments=args.attachments)
                                json_records.append(rec)
                                processed += 1
                                _progress_emit(progress_path, {"phase": "processed", "kind": "pst-eml", "file": rec["source"], "processed": processed})
                                _add_hash_row("message", rec["source"], rec["file"], None, rec.get("source_sha256"))
                                for a in rec.get("attachments", []) or []:
                                    _add_hash_row("attachment", rec["source"], a.get("filename",""), a.get("size"), a.get("sha256"))
                            except Exception:
                                errors += 1
                                out.write("="*90 + "\n")
                                out.write(f"ERROR reading extracted message from {pst}:\n")
                                out.write(traceback.format_exc())
                                out.write("="*90 + "\n\n")
                                print(f"[ERROR] Failed extracted message from {pst}")
                    except Exception:
                        errors += 1
                        out.write("="*90 + "\n")
                        out.write(f"ERROR converting PST {pst}:\n")
                        out.write(traceback.format_exc())
                        out.write("="*90 + "\n\n")
                        print(f"[ERROR] Failed .pst: {pst}")

    if (not args.no_json) and json_records:
        try:
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump({"source_root": str(input_path), "output_text": str(out_path), "messages": json_records}, jf, ensure_ascii=False, indent=2)
            print(f"[INFO] JSON log written: {json_path}")
        except Exception as e:
            print(f"[WARN] Could not write JSON log: {e}")

    if hashes_enabled and hashes_path and hash_rows:
        try:
            with open(hashes_path, "w", newline="", encoding="utf-8") as cf:
                w = csv.writer(cf)
                w.writerow(["type","parent_source","filename","size","sha256"])
                w.writerows(hash_rows)
            print(f"[INFO] Hashes CSV written: {hashes_path}")
        except Exception as e:
            print(f"[WARN] Could not write hashes CSV: {e}")

    _progress_emit(progress_path, {"phase": "done", "processed": processed, "errors": errors})
    print(f"[DONE] Wrote {processed} message(s) to: {out_path}")
    if errors: print(f"[NOTE] {errors} item(s) had errors. Details are logged in the output file.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
