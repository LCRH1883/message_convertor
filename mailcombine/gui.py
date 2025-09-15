from __future__ import annotations
import sys, json, time, tempfile, threading
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QTextEdit, QCheckBox, QProgressBar
)
from PySide6.QtCore import QThread, Signal

from mailcombine.cli import main as cli_main


class Worker(QThread):
    done = Signal(int)
    def __init__(self, input_path: str, output_path: str,
                 show_attachments: bool, write_json: bool,
                 write_hashes: bool, progress_path: str, hashes_csv: str | None):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.show_attachments = show_attachments
        self.write_json = write_json
        self.write_hashes = write_hashes
        self.progress_path = progress_path
        self.hashes_csv = hashes_csv

    def run(self):
        argv = ["-i", self.input_path, "-o", self.output_path, "--progress-file", self.progress_path]
        if self.show_attachments: argv.append("--attachments")
        if not self.write_json: argv.append("--no-json")
        if self.write_hashes:
            argv.append("--hashes")
            if self.hashes_csv: argv.extend(["--hashes-path", self.hashes_csv])
        try:
            rc = cli_main(argv)
        except SystemExit as e:
            rc = int(e.code)
        except Exception:
            rc = 1
        self.done.emit(rc)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MsgSecure")
        self.resize(780, 540)

        lay = QVBoxLayout(self)

        in_row = QHBoxLayout()
        self.in_edit = QLineEdit()
        self.in_btn = QPushButton("Browse…")
        in_row.addWidget(QLabel("Input Folder:")); in_row.addWidget(self.in_edit, 1); in_row.addWidget(self.in_btn)
        lay.addLayout(in_row)

        out_row = QHBoxLayout()
        self.out_edit = QLineEdit()
        self.out_btn = QPushButton("Save As…")
        out_row.addWidget(QLabel("Output File:")); out_row.addWidget(self.out_edit, 1); out_row.addWidget(self.out_btn)
        lay.addLayout(out_row)

        opt_row1 = QHBoxLayout()
        self.attach_cb = QCheckBox("Include attachments in text")
        self.json_cb = QCheckBox("Write JSON sidecar"); self.json_cb.setChecked(True)
        opt_row1.addWidget(self.attach_cb); opt_row1.addWidget(self.json_cb); opt_row1.addStretch(1)
        lay.addLayout(opt_row1)

        opt_row2 = QHBoxLayout()
        self.hashes_cb = QCheckBox("Write hashes.csv (SHA-256)")
        opt_row2.addWidget(self.hashes_cb); opt_row2.addStretch(1)
        lay.addLayout(opt_row2)

        self.progress = QProgressBar(); self.progress.setRange(0, 100); lay.addWidget(self.progress)
        self.run_btn = QPushButton("Run"); lay.addWidget(self.run_btn)
        self.log = QTextEdit(); self.log.setReadOnly(True); lay.addWidget(self.log, 1)

        self.in_btn.clicked.connect(self.pick_input)
        self.out_btn.clicked.connect(self.pick_output)
        self.run_btn.clicked.connect(self.run_task)

        self._stop_poll = threading.Event()

    def pick_input(self):
        d = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if d: self.in_edit.setText(d)

    def pick_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output Text", "combined_emails.txt", "Text Files (*.txt);;All Files (*)")
        if path: self.out_edit.setText(path)

    def run_task(self):
        inp = self.in_edit.text().strip()
        outp = self.out_edit.text().strip() or str(Path.cwd() / "combined_emails.txt")
        self.progress_path = str(Path(tempfile.gettempdir()) / f"mailcombine_progress_{int(time.time())}.jsonl")
        hashes_path = str(Path(outp).with_suffix("").as_posix() + "_hashes.csv") if self.hashes_cb.isChecked() else None

        self.worker = Worker(inp, outp, self.attach_cb.isChecked(), self.json_cb.isChecked(),
                             self.hashes_cb.isChecked(), self.progress_path, hashes_path)
        self.run_btn.setEnabled(False)
        self.worker.done.connect(self.on_done)
        self.worker.start()
        self.log.append("[INFO] Started…")
        self._stop_poll.clear()
        threading.Thread(target=self.poll_progress, daemon=True).start()

    def poll_progress(self):
        total_known = None; processed = 0; pst_mode = False
        self.set_busy(True)
        last_text = ""
        while not self._stop_poll.is_set():
            try:
                p = Path(self.progress_path)
                if p.exists():
                    data = p.read_text("utf-8")
                    if data != last_text:
                        last_text = data
                        for line in data.splitlines():
                            try: msg = json.loads(line)
                            except Exception: continue
                            if msg.get("phase") == "scan":
                                total_known = int(msg.get("msg", 0)) + int(msg.get("eml", 0))
                                processed = 0; pst_mode = False
                                self.log_append(f"[SCAN] msg={msg.get('msg',0)} eml={msg.get('eml',0)} pst={msg.get('pst',0)}")
                                self.set_busy(total_known <= 0)
                                if total_known > 0: self.update_progress(processed, total_known)
                            elif msg.get("phase") == "processed":
                                processed += 1
                                if not pst_mode and total_known and total_known > 0:
                                    self.update_progress(processed, total_known)
                                else:
                                    self.set_busy(True)
                            elif msg.get("phase") == "pst_start":
                                pst_mode = True; self.set_busy(True); self.log_append("[INFO] Converting PST…")
                            elif msg.get("phase") == "pst_extracted":
                                self.log_append(f"[PST] Extracted {msg.get('count',0)} from {msg.get('pst','')}")
                            elif msg.get("phase") == "pst_skipped":
                                self.log_append("[WARN] PST skipped (no embedded readpst).")
                            elif msg.get("phase") == "done":
                                self.set_busy(False); self.progress.setValue(100)
                                self.log_append(f"[DONE] processed={msg.get('processed',0)} errors={msg.get('errors',0)}")
                                self._stop_poll.set(); break
            except Exception:
                pass
            time.sleep(0.2)

    def set_busy(self, busy: bool):
        self.progress.setRange(0, 0) if busy else self.progress.setRange(0, 100)

    def update_progress(self, processed, total):
        pct = max(0, min(100, int(processed * 100 / max(1, total))))
        self.progress.setValue(pct)

    def log_append(self, text: str): self.log.append(text)

    def on_done(self, rc: int):
        self.log.append(f"[EXIT] Code {rc}")
        self.run_btn.setEnabled(True)
        self._stop_poll.set()

def main():
    app = QApplication(sys.argv)
    w = App(); w.show()
    sys.exit(app.exec())
