# Email Searcher v0.0.1

**Author:** AntiCrypto

A lightweight Python desktop GUI application (`tkinter`) that scans text files across a chosen directory for email addresses, filters by full address or domain, and exports results to a `.txt` file.

## Features

- **GUI Search Interface:** Pick any target folder, filter by exact email or domain (e.g., `@example.com`), or leave blank to extract all matching addresses.
- **Customizable Extensions:** Scan `.txt`, `.log`, `.csv`, `.json`, `.xml`, `.md`, `.sql`, `.py`, `.html`, and more.
- **Background Scanning:** Runs directory traversal in a worker thread with a **Stop** button and optional skipping of system/cache directories.
- **Result Export:** Save matches with file paths and line numbers to a text file.

## Run From Source

Requires Python 3.10+ (uses standard library `tkinter`):

```bash
python email_searcher.py