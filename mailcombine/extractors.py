from __future__ import annotations
import sys, os, tempfile, subprocess, platform, shutil, re, hashlib
from pathlib import Path
try:
    from importlib.resources import files as pkg_files, as_file
except ImportError:  # Python < 3.9
    try:
        from importlib_resources import files as pkg_files, as_file  # type: ignore
    except ImportError:
        pkg_files = None  # type: ignore
        as_file = None  # type: ignore

from .extractors_readpst_fallback import resolve_readpst_path

try:
    import extract_msg
except ImportError:
    extract_msg = None

def clean_text(s):
    if s is None:
        return ""
    if not isinstance(s, str):
        try:
            if hasattr(s, "isoformat"):
                s = s.isoformat()
            else:
                s = str(s)
        except Exception:
            s = str(s)
    return s.replace("\r\n", "\n").replace("\r", "\n").strip()

def html_to_text(html: str) -> str:
    if not html: return ""
    textish = re.sub(r"(?is)<(script|style).*?</\1>", "", html)
    textish = re.sub(r"(?is)<br\s*/?>", "\n", textish)
    textish = re.sub(r"(?is)</p\s*>", "\n\n", textish)
    textish = re.sub(r"(?is)<.*?>", "", textish)
    return clean_text(textish)

def try_getattr(obj, name, default=None):
    try: return getattr(obj, name)
    except Exception: return default

def _sha256_bytes(data: bytes | None) -> str | None:
    if data is None: return None
    h = hashlib.sha256(); h.update(data); return h.hexdigest()

def _sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024*1024), b""): h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

# ---- .msg ----
def extract_from_msg(msg_path: Path) -> dict:
    if extract_msg is None:
        raise RuntimeError("The 'extract-msg' package is not installed.")
    m = extract_msg.Message(str(msg_path))

    date_raw = try_getattr(m, "date", "")
    date_ = date_raw.isoformat() if hasattr(date_raw, "isoformat") else (str(date_raw) if date_raw is not None else "")

    sender = try_getattr(m, "sender", "") or ""
    to_ = try_getattr(m, "to", "") or ""
    subject = try_getattr(m, "subject", "") or ""
    msgid = try_getattr(m, "message_id", "") or ""

    body = try_getattr(m, "body", "") or ""
    if not body:
        html_body = try_getattr(m, "htmlBody", "") or ""
        if html_body: body = html_to_text(html_body)

    atts = []
    for a in (getattr(m, "attachments", None) or []):
        name = getattr(a, "longFilename", None) or getattr(a, "shortFilename", None) or getattr(a, "filename", None) or "attachment"
        data = None
        try: data = a.data
        except Exception:
            try: data = a.getData()
            except Exception: data = None
        size = len(data) if isinstance(data, (bytes, bytearray)) else None
        sha = _sha256_bytes(data) if data else None
        atts.append({"filename": name, "size": size, "sha256": sha})

    return {
        "file": msg_path.name,
        "source": str(msg_path),
        "date": clean_text(date_),
        "from": clean_text(sender),
        "to": clean_text(to_),
        "subject": clean_text(subject),
        "message_id": clean_text(msgid),
        "body": clean_text(body) if body else "(No Body Extracted)",
        "attachments": atts,
        "source_sha256": _sha256_file(msg_path),
    }

# ---- .eml ----
def extract_from_eml(eml_path: Path) -> dict:
    import email
    from email import policy
    from email.parser import BytesParser
    with open(eml_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    date_ = clean_text(msg.get("Date"))
    sender = clean_text(msg.get("From"))
    to_ = clean_text(msg.get("To"))
    subject = clean_text(msg.get("Subject"))
    msgid = clean_text(msg.get("Message-ID"))

    body_text = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_disposition() == "attachment": continue
            if part.get_content_type() == "text/plain":
                body_text = clean_text(part.get_content()); break
        if not body_text:
            for part in msg.walk():
                if part.get_content_disposition() == "attachment": continue
                if part.get_content_type() == "text/html":
                    body_text = html_to_text(part.get_content()); break
    else:
        ctype = msg.get_content_type()
        if ctype == "text/plain": body_text = clean_text(msg.get_content())
        elif ctype == "text/html": body_text = html_to_text(msg.get_content())
    if not body_text: body_text = "(No Body Extracted)"

    atts = []
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            name = part.get_filename() or "attachment"
            payload = None
            try: payload = part.get_payload(decode=True)
            except Exception: payload = None
            size = len(payload) if isinstance(payload, (bytes, bytearray)) else None
            sha = _sha256_bytes(payload) if payload else None
            atts.append({"filename": name, "size": size, "sha256": sha})

    return {
        "file": eml_path.name,
        "source": str(eml_path),
        "date": date_,
        "from": sender,
        "to": to_,
        "subject": subject,
        "message_id": msgid,
        "body": body_text,
        "attachments": atts,
        "source_sha256": _sha256_file(eml_path),
    }

# ---- PST (embedded readpst) ----
def has_embedded_readpst() -> bool:
    p = _get_embedded_readpst_path()
    if os.environ.get("MSGSECURE_DEBUG"):
        print(f"[debug] readpst -> {p}")
    return bool(p and Path(p).is_file())

def _get_embedded_readpst_path():
    """
    Return a real Path to the embedded readpst binary if present.
    Tries importlib.resources first, then PyInstaller _MEIPASS fallbacks.
    Also allows MSGSECURE_READPST to override.
    """
    # explicit override (let devs force a path)
    env_override = os.environ.get("MSGSECURE_READPST")
    if env_override:
        p = Path(env_override)
        if p.is_file():
            return p

    system = platform.system().lower()
    plat_dir = "win64" if system.startswith("win") else ("linux64" if system.startswith("linux") else None)
    exe_name = "readpst.exe" if system.startswith("win") else "readpst"
    if plat_dir is None:
        return None

    # 1) importlib.resources route (works in src and many frozen cases)
    if pkg_files and as_file:
        try:
            base = pkg_files("mailcombine") / "resources" / plat_dir
            cand = base / exe_name
            with as_file(cand) as real_path:
                rp = Path(real_path)
                if rp.is_file():
                    return rp
        except Exception:
            pass

    # 2) PyInstaller _MEIPASS (onefile)
    try:
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            for rel in (
                os.path.join("mailcombine", "resources", plat_dir, exe_name),
                os.path.join("resources", plat_dir, exe_name),
                os.path.join(plat_dir, exe_name),
            ):
                p = Path(meipass) / rel
                if p.is_file():
                    return p
    except Exception:
        pass

    # 3) last-resort: adjacent to this file (onefolder dev runs)
    here = Path(__file__).resolve().parent
    fallback = here / "resources" / plat_dir / exe_name
    if fallback.is_file():
        return fallback

    return None

def _stage_readpst_to_temp() -> Path:
    embedded_src = _get_embedded_readpst_path()
    resolved = resolve_readpst_path(_get_embedded_readpst_path)
    if not resolved:
        raise RuntimeError("PST support is not available in this build (readpst executable not found).")
    resolved_path = Path(resolved)

    use_embedded = False
    if embedded_src:
        try:
            use_embedded = os.path.samefile(str(embedded_src), str(resolved_path))
        except Exception:
            use_embedded = Path(embedded_src) == resolved_path

    if use_embedded:
        if platform.system().lower().startswith("win"):
            return resolved_path
        tdir = Path(tempfile.mkdtemp(prefix="readpst_"))
        dst = tdir / resolved_path.name
        with open(embedded_src, "rb") as fsrc, open(dst, "wb") as fdst:
            shutil.copyfileobj(fsrc, fdst)
        if platform.system().lower().startswith("linux"):
            os.chmod(dst, 0o755)
        return dst

    return resolved_path

def iter_eml_paths_from_pst(pst_path: Path, temp_root: Path):
    readpst = _stage_readpst_to_temp()
    out_dir = temp_root / (pst_path.stem + "_readpst")
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [str(readpst), "-r", "-D", "-e", "-o", str(out_dir), str(pst_path)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(
            f"readpst failed ({proc.returncode})\n"
            f"STDOUT:\n{proc.stdout.decode(errors='replace')}\n\n"
            f"STDERR:\n{proc.stderr.decode(errors='replace')}"
        )
    for p in sorted(out_dir.rglob("*.eml")):
        yield p
