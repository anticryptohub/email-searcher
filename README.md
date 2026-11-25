# Email Searcher v0.0.2

**Author:** AntiCrypto

A lightweight Python desktop GUI application (`tkinter`) that scans text files across a chosen directory for email addresses, removes duplicates, and exports results using customizable formats and delimiters.

## Features

- **Splash Screen Loader:** Dark-themed startup screen with initialization progress before launching the main window.
- **GUI Search Interface:** Pick any target folder, filter by exact email or domain (e.g., `@example.com`), or leave blank to extract all matching addresses.
- **Duplicate Email Removal:**
  - Toggle **Remove duplicate emails** to filter duplicates live during a scan or dynamically hide/show duplicates in existing results.
  - Click **Deduplicate Now** to permanently purge duplicate entries from the current result set.
- **Flexible Export Options:**
  - Export **Emails only** (clean list) or **Full details** (`filepath:line -> email`).
  - Choose from built-in delimiters (**New Line**, **Comma**, **Comma + Space**, **Semicolon**, **Pipe**, **Tab**, **Space**) or define a **Custom** separator.
  - Optional case-insensitive deduplication at export time.
- **Customizable Extensions & Background Scanning:** Scan `.txt`, `.log`, `.csv`, `.json`, `.xml`, `.md`, `.sql`, `.py`, `.html`, and more in a non-blocking worker thread with **Stop** support and optional skipping of system/cache directories.

## Run From Source

Requires Python 3.10+ (uses standard library `tkinter`):

```bash
python email_searcher.py
