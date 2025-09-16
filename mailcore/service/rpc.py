"""Lightweight JSON-RPC server exposing mailcore functions."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

from .. import load_mailbox, load_single_message
from ..exporters import export_hashes, export_json, export_text
from ..serialization import dict_to_message, mailbox_to_dict, message_to_dict


class MailcoreJsonRpcServer:
    def __init__(self, instream=None, outstream=None):
        self.instream = instream or sys.stdin
        self.outstream = outstream or sys.stdout
        self._running = True
        self.handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {
            "ping": self.handle_ping,
            "shutdown": self.handle_shutdown,
            "load_mailbox": self.handle_load_mailbox,
            "load_message": self.handle_load_message,
            "export_text": self.handle_export_text,
            "export_json": self.handle_export_json,
            "export_hashes": self.handle_export_hashes,
            "export_bundle": self.handle_export_bundle,
        }

    def serve_forever(self) -> None:
        while self._running:
            line = self.instream.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            response = self._process_line(line)
            self.outstream.write(json.dumps(response) + "\n")
            self.outstream.flush()

    def _process_line(self, line: str) -> Dict[str, Any]:
        request: Dict[str, Any] = {}
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params") or {}
            request_id = request.get("id")
            if method not in self.handlers:
                raise ValueError(f"Unknown method: {method}")
            result = self.handlers[method](params)
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id") if isinstance(request, dict) else None,
                "error": {"code": -32603, "message": str(exc)},
            }

    def handle_ping(self, params: Dict[str, Any]) -> str:
        return "pong"

    def handle_shutdown(self, params: Dict[str, Any]) -> Dict[str, str]:
        self._running = False
        return {"status": "closing"}

    def handle_load_mailbox(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = Path(params["path"])
        mailbox = load_mailbox(path)
        return mailbox_to_dict(mailbox)

    def handle_load_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = Path(params["path"])
        message = load_single_message(path)
        return message_to_dict(message)

    def _messages_from_params(self, params: Dict[str, Any]) -> List:
        message_dicts = params.get("messages")
        if message_dicts:
            return [dict_to_message(data) for data in message_dicts]
        paths = params.get("paths", [])
        return [load_single_message(Path(p)) for p in paths]

    def handle_export_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        messages = self._messages_from_params(params)
        dest = Path(params["dest"])
        source = params.get("source", "")
        show_attachments = bool(params.get("show_attachments", False))
        encoding = params.get("encoding", "utf-8")
        export_text(messages, dest, source_label=source, show_attachments=show_attachments, encoding=encoding)
        return {"written": str(dest)}

    def handle_export_json(self, params: Dict[str, Any]) -> Dict[str, Any]:
        messages = self._messages_from_params(params)
        dest = Path(params["dest"])
        source = params.get("source", "")
        output_text = Path(params.get("output_text", "")) if params.get("output_text") else Path()
        export_json(messages, dest, source_label=source, output_text_path=output_text)
        return {"written": str(dest)}

    def handle_export_hashes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        messages = self._messages_from_params(params)
        dest = Path(params["dest"])
        export_hashes(messages, dest)
        return {"written": str(dest)}

    def handle_export_bundle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        messages = self._messages_from_params(params)
        if not messages:
            raise ValueError("No messages provided for export")
        source = params.get("source", "")
        show_attachments = bool(params.get("show_attachments", False))
        encoding = params.get("encoding", "utf-8")
        text_path = Path(params["text_path"])
        export_text(messages, text_path, source_label=source, show_attachments=show_attachments, encoding=encoding)
        result = {"text": str(text_path)}
        if params.get("write_json"):
            json_path = params.get("json_path")
            if json_path:
                export_json(messages, Path(json_path), source_label=source, output_text_path=text_path)
                result["json"] = json_path
        if params.get("write_hashes"):
            hashes_path = params.get("hashes_path")
            if hashes_path:
                export_hashes(messages, Path(hashes_path))
                result["hashes"] = hashes_path
        return result


def main() -> None:
    server = MailcoreJsonRpcServer()
    server.serve_forever()


if __name__ == "__main__":
    main()
