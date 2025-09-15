from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal

from .cli import main as cli_main

class Worker(QThread):
    log = Signal(str)
    done = Signal(int)

    def __init__(self, input_path: str, output_path: str, show_attachments: bool, write_json: bool):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.show_attachments = show_attachments
        self.write_json = write_json

    def run(self):
        argv = [
            "-i", self.input_path,
            "-o", self.output_path,
        ]
        if self.show_attachments:
            argv.append("--attachments")
        if not self.write_json:
            argv.append("--no-json")
        try:
            rc = cli_main(argv)
        except SystemExit as e:
            rc = int(e.code)
        except Exception as e:
            rc = 1
            self.log.emit(f"[ERROR] {e}")
        self.done.emit(rc)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mail Combine")
        self.resize(720, 480)

        lay = QVBoxLayout(self)

        # Input
        in_row = QHBoxLayout()
        self.in_edit = QLineEdit()
        self.in_btn = QPushButton("Browse…")
        in_row.addWidget(QLabel("Input Folder:"))
        in_row.addWidget(self.in_edit, 1)
        in_row.addWidget(self.in_btn)
        lay.addLayout(in_row)

        # Output
        out_row = QHBoxLayout()
        self.out_edit = QLineEdit()
        self.out_btn = QPushButton("Save As…")
        out_row.addWidget(QLabel("Output File:"))
        out_row.addWidget(self.out_edit, 1)
        out_row.addWidget(self.out_btn)
        lay.addLayout(out_row)

        # Options
        opt_row = QHBoxLayout()
        self.attach_cb = QCheckBox("Include attachments in text")
        self.json_cb = QCheckBox("Write JSON sidecar")
        self.json_cb.setChecked(True)
        opt_row.addWidget(self.attach_cb)
        opt_row.addWidget(self.json_cb)
        opt_row.addStretch(1)
        lay.addLayout(opt_row)

        # Run button
        self.run_btn = QPushButton("Run")
        lay.addWidget(self.run_btn)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        lay.addWidget(self.log, 1)

        # Signals
        self.in_btn.clicked.connect(self.pick_input)
        self.out_btn.clicked.connect(self.pick_output)
        self.run_btn.clicked.connect(self.run_task)

    def pick_input(self):
        d = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if d:
            self.in_edit.setText(d)

    def pick_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output Text", "combined_emails.txt", "Text Files (*.txt);;All Files (*)")
        if path:
            self.out_edit.setText(path)

    def run_task(self):
        inp = self.in_edit.text().strip()
        outp = self.out_edit.text().strip() or str(Path.cwd() / "combined_emails.txt")
        self.worker = Worker(inp, outp, self.attach_cb.isChecked(), self.json_cb.isChecked())
        self.run_btn.setEnabled(False)
        self.worker.done.connect(self.on_done)
        self.worker.start()
        self.log.append("[INFO] Started…")

    def on_done(self, rc: int):
        self.log.append(f"[DONE] Exit code {rc}")
        self.run_btn.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())
