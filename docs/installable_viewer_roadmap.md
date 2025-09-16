# Installable msgsecure Viewer Roadmap

## 1. mailcore Shared Library

### 1.1 Goals
- Single source of truth for message ingestion, normalization, and export workflows.
- Reusable from existing Python CLI/portable GUI today, with a migration path to a future .NET implementation.
- Testable units covering parsing and export behaviours across PST/OST/MSG/EML.

### 1.2 Immediate Bootstrap (Python)
1. Create `mailcore/` package alongside existing `mailcombine`.
2. Define neutral models in `mailcore/models.py`:
   - `Mailbox`, `Folder`, `Message`, `Attachment`, `BodyPart`, `HashInfo`.
   - Typed dataclasses with serialization helpers.
3. Implement adapters in `mailcore/adapters/`:
   - `pst_reader.py`: wraps current `iter_eml_paths_from_pst` + extractors to populate models.
   - `msg_reader.py`, `eml_reader.py`: leverage existing functions (`extract_from_msg`, `extract_from_eml`).
   - Provide async-friendly facades using `concurrent.futures` to keep UI responsive.
4. Central facade `mailcore/api.py`:
   - `open_mailbox(path: Path) -> Mailbox` (detect PST/OST/MSG/EML set).
   - `list_messages(folder)` and `get_message_content(message_id)`.
   - `export(messages, format, options)` delegating to exporters.
5. Move exporter logic from `mailcombine/writer.py` and CLI into `mailcore/exporters/`:
   - `text.py`, `html.py`, `pdf.py`, `eml_passthrough.py`, `hash_report.py`.
   - Register via `mailcore/export_registry.py` mapping format enum → strategy.
6. Maintain backward compatibility:
   - Update existing CLI/GUI to import from `mailcore` facades.
   - Provide thin shims in `mailcombine` for interim period.
7. Testing:
   - Introduce `tests/mailcore/` with fixtures covering PST sample, MSG, EML.
   - Use pytest parameterized cases to verify exporters produce identical output to legacy paths.

### 1.3 Future .NET Port Option
- Mirror Python dataclasses with C# records in a .NET Standard project (`Mailcore.Net`).
- Expose gRPC or REST bridge if mixed-language support is required during migration.
- Plan for drop-in replacement: interface definitions (`IMailboxProvider`, `IExporter`) shared via OpenAPI or protobuf.

## 2. Windows Viewer (WPF/WinUI)

### 2.1 Project Setup
- New solution `msgsecure-viewer.sln` (WPF on .NET 8).
- Projects:
  - `Mailcore.Net` (future port, placeholder referencing Python via REST/CLI during bootstrap).
  - `MsgSecure.Viewer` (WPF UI).
  - `MsgSecure.Viewer.Tests` (UI logic tests using xUnit + FluentAssertions).
- Dependency injection with `Microsoft.Extensions.DependencyInjection`.

### 2.2 Shell UI Scaffold
1. MainWindow layout (Tabbed for future multi-open):
   - Left: `TreeView` for folder hierarchy.
   - Center: `DataGrid`/`ListView` for messages.
   - Right/Btm: `Frame` hosting HTML preview (WebView2) + metadata panel.
2. ViewModels:
   - `ShellViewModel` orchestrating services, loading state, commands (`OpenCommand`, `ExportCommand`).
   - `FolderViewModel`, `MessageViewModel`, `AttachmentViewModel` mapping `mailcore` models.
3. Services:
   - `IMailboxService` → concrete `MailcoreMailboxService` calling Python `mailcore` via CLI/HTTP (initial).
   - `IExportService` → leverages shared export pipeline.
4. UX considerations:
   - Async load with `Task.Run`, progress overlays.
   - Error surface via dialog service.
   - Recently opened list persisted (JSON settings).

### 2.3 Interop Strategy (Interim)
- Host Python `mailcore` as background process with simple JSON-RPC over stdin/stdout (reuse CLI entry points).
- Provide stub interfaces ready to swap with native C# implementation once ported.

## 3. Export Dialog & Progress

### 3.1 Requirements
- Match portable tool features (format selection, per-message vs merged, hashes).
- Provide preview of file naming, destination selection, overwrite options with "Apply to all".
- Display progress + ability to cancel.

### 3.2 Implementation Outline
1. Export dialog (`ExportDialog.xaml`) with:
   - Format dropdown (bound to `ExportFormat` enum).
   - Checkboxes for `IncludeAttachments`, `GenerateHashReport`, `MergeIntoSingleFile`.
   - Destination picker (folder/file depending on merge option).
2. Export pipeline service:
   - Accepts `ExportRequest` (messages + options + cancellation token).
   - Streams work to background thread, reporting via `IProgress<ExportProgress>` (current/total, file path, status).
   - Hash reporting reuses `hash_report.py` implementation through `mailcore`.
3. UI wiring:
   - Progress dialog showing bar + log lines; support cancellation (propagate to Python process or .NET exporter).
   - Completion summary (success count, failures, hash file location).
4. Automated tests to ensure exporter options map correctly (mock `IMailcoreExporter`).

## 4. Packaging & Testing

### 4.1 Installer Packaging
- Use `dotnet publish MsgSecure.Viewer -c Release -r win-x64 --self-contained true /p:PublishSingleFile=true /p:IncludeNativeLibrariesForSelfExtract=true`.
- Wrap output with Inno Setup script (`packaging/msgsecure_viewer.iss`) to create single EXE installer:
  - Install to `%ProgramFiles%\MsgSecure Viewer`.
  - Add Start Menu shortcut, file associations (.pst, .ost, .msg, .eml).
  - Bundle dependencies (WebView2 Evergreen bootstrapper optional).
  - Code-sign using organization certificate.

### 4.2 Smoke Tests
- VM matrix: Windows 10 22H2, Windows 11 24H2.
- Test cases:
  1. Clean install, launch, open 5GB PST (observe load times, memory usage).
  2. Open password-protected PST (expect prompt via XstReader support).
  3. Drag/drop multiple MSG/EML files.
  4. Export 1000-message folder to PDF (merged and per-message) with hashes.
  5. Uninstall cleans entries.
- Capture metrics (CPU/memory) and log issues for performance tuning.

### 4.3 Automation Hooks
- Add GitHub Actions workflow to run `dotnet build` + Python tests + package artifacts.
- Nightly job publishes installer to internal feed for QA.

## 5. Next Actions Checklist
- [ ] Scaffold `mailcore` package + dataclasses.
- [ ] Relocate exporter logic + update existing CLI imports.
- [ ] Prototype JSON-RPC bridge for WPF to call Python services.
- [ ] Initialise WPF solution with DI + basic open file command.
- [ ] Draft export dialog UI and wire to placeholders.
- [ ] Author Inno Setup script template.
- [ ] Define smoke-test scripts/documentation.

