# Mailcore JSON-RPC Bridge

This lightweight service allows external applications (e.g. the future WPF viewer) to
communicate with the Python `mailcore` package without embedding Python directly.

## Starting the server

```powershell
python -m mailcore.rpc_server
```

The server listens on **STDIN/STDOUT** using newline-delimited JSON-RPC 2.0 messages. Each
request/response is a single JSON object per line.

## Supported Methods

| Method           | Params                                                                                   | Result Description                       |
|------------------|-------------------------------------------------------------------------------------------|------------------------------------------|
| `ping`           | `{}`                                                                                      | `{ "result": "pong" }`                 |
| `shutdown`       | `{}`                                                                                      | `{ "status": "closing" }` (server exits)|
| `load_mailbox`   | `{ "path": "C:\\path\\to\\source" }`                                              | Serialized mailbox (folders/messages)    |
| `load_message`   | `{ "path": "C:\\path\\to\\message.eml" }`                                        | Serialized single message                |
| `export_text`    | `{ "messages": [...], "dest": "out.txt", "source": "label", "show_attachments": true }` | Writes text export and returns path      |
| `export_json`    | `{ "messages": [...], "dest": "out.json", "source": "label", "output_text": "out.txt" }` | Writes JSON sidecar and returns path    |
| `export_hashes`  | `{ "messages": [...], "dest": "hashes.csv" }`                                         | Writes hashes CSV and returns path       |

> **Note:** `messages` is a list of message objects previously returned by `load_mailbox`
or `load_message`. When `messages` is omitted you may supply `paths` (list of `.msg/.eml`
files) for convenience.

## Message shape

Responses use JSON-friendly dictionaries produced by the serialization helpers (paths and
timestamps are represented as strings). The client can send these objects back in the
`messages` parameter when invoking export methods.

## Example Session

```
{"id": 1, "jsonrpc": "2.0", "method": "ping"}
{"id": 1, "jsonrpc": "2.0", "result": "pong"}
{"id": 2, "jsonrpc": "2.0", "method": "load_mailbox", "params": {"path": "sample.pst"}}
{"id": 2, "jsonrpc": "2.0", "result": { ... mailbox data ... }}
{"id": 3, "jsonrpc": "2.0", "method": "shutdown"}
{"id": 3, "jsonrpc": "2.0", "result": {"status": "closing"}}
```

This bridge keeps the viewer development unblocked while the .NET port of `mailcore`
progresses.
