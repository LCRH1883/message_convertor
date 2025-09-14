from __future__ import annotations
import sys, argparse, tempfile, traceback
from pathlib import Path

from .writer import write_record, write_header
from .extractors import (
    extract_from_msg, extract_from_eml,
    iter_eml_paths_from_pst, has_embedded_readpst
)

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Combine .msg, .eml, and .pst emails into a single searchable .txt file."
    )
    parser.add_argument("-i", "--input", default="msg_files", help="Root folder to search recursively")
    parser.add_argument("-o", "--output", default="combined_emails.txt", help="Output text file")
    parser.add_argument("--encoding", default="utf-8", help="Output encoding (default utf-8)")
    args = parser.parse_args(argv)

    in_dir = Path(args.input).expanduser().resolve()
    out_path = Path(args.output).expanduser().resolve()

    print(f"[INFO] Input folder: {in_dir}")
    print(f"[INFO] Output file : {out_path}")
    if not in_dir.exists():
        print(f"[ERROR] Input folder does not exist: {in_dir}")
        return 2

    msg_files = sorted(p for p in in_dir.rglob("*.msg") if p.is_file())
    eml_files = sorted(p for p in in_dir.rglob("*.eml") if p.is_file())
    pst_files = sorted(p for p in in_dir.rglob("*.pst") if p.is_file())

    print(f"[INFO] Found {len(msg_files)} .msg, {len(eml_files)} .eml, {len(pst_files)} .pst")

    processed = 0
    errors = 0

    with open(out_path, "w", encoding=args.encoding, errors="replace") as out:
        write_header(out, str(in_dir))

        # .msg
        for idx, p in enumerate(msg_files, 1):
            print(f"[INFO] (.msg {idx}/{len(msg_files)}) {p}")
            try:
                rec = extract_from_msg(p)
                write_record(out, rec)
                processed += 1
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
                rec = extract_from_eml(p)
                write_record(out, rec)
                processed += 1
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
            else:
                with tempfile.TemporaryDirectory(prefix="pst_extract_") as tdir:
                    troot = Path(tdir)
                    for idx, pst in enumerate(pst_files, 1):
                        print(f"[INFO] (.pst {idx}/{len(pst_files)}) {pst}")
                        try:
                            extracted = list(iter_eml_paths_from_pst(pst, troot))
                            print(f"[INFO]   Extracted {len(extracted)} message(s) from {pst.name}")
                            for eidx, eml in enumerate(extracted, 1):
                                try:
                                    rec = extract_from_eml(eml)
                                    # Include PST source for chain-of-custody clarity
                                    rec['source'] = f"{pst} :: {eml}"
                                    write_record(out, rec)
                                    processed += 1
                                except Exception:
                                    errors += 1
                                    out.write("="*90 + "\n")
                                    out.write(f"ERROR reading extracted EML from {pst} -> {eml}:\n")
                                    out.write(traceback.format_exc())
                                    out.write("="*90 + "\n\n")
                                    print(f"[ERROR] Failed extracted .eml: {eml}")
                        except Exception:
                            errors += 1
                            out.write("="*90 + "\n")
                            out.write(f"ERROR converting PST {pst}:\n")
                            out.write(traceback.format_exc())
                            out.write("="*90 + "\n\n")
                            print(f"[ERROR] Failed .pst: {pst}")

    print(f"[DONE] Wrote {processed} message(s) to: {out_path}")
    if errors:
        print(f"[NOTE] {errors} item(s) had errors. Details are logged in the output file.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())