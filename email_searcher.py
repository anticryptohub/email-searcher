"""
Email Searcher v0.0.2 by AntiCrypto
Scans text files on your PC for matching email addresses with a desktop GUI,
splash screen loader, deduplication, and flexible export formatting.
"""

import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

DEFAULT_EXTENSIONS = {
    ".txt",
    ".log",
    ".csv",
    ".tsv",
    ".json",
    ".xml",
    ".yaml",
    ".yml",
    ".md",
    ".rtf",
    ".ini",
    ".cfg",
    ".conf",
    ".sql",
    ".py",
    ".js",
    ".ts",
    ".html",
    ".htm",
}

SKIP_DIRS = {
    "$Recycle.Bin",
    "System Volume Information",
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "ProgramData",
    "AppData",
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    ".venv",
}

DELIMITERS = {
    "New Line (\\n)": "\n",
    "Comma (,)": ",",
    "Comma + Space (, )": ", ",
    "Semicolon (;)": ";",
    "Semicolon + Space (; )": "; ",
    "Pipe (|)": "|",
    "Tab (\\t)": "\t",
    "Space ( )": " ",
}


class SplashScreen:
    def __init__(self, root: tk.Tk, on_complete) -> None:
        self.root = root
        self.on_complete = on_complete

        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)
        self.splash.attributes("-topmost", True)

        width, height = 440, 230
        screen_w = self.splash.winfo_screenwidth()
        screen_h = self.splash.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.splash.geometry(f"{width}x{height}+{x}+{y}")

        container = tk.Frame(
            self.splash,
            bg="#12161f",
            highlightbackground="#2b6cb0",
            highlightthickness=2,
        )
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="EMAIL SEARCHER",
            font=("Segoe UI", 20, "bold"),
            fg="#63b3ed",
            bg="#12161f",
        ).pack(pady=(34, 2))

        tk.Label(
            container,
            text="v0.0.2  •  by AntiCrypto",
            font=("Segoe UI", 10, "italic"),
            fg="#a0aec0",
            bg="#12161f",
        ).pack(pady=(0, 26))

        self.step_var = tk.StringVar(value="Initializing engine...")
        tk.Label(
            container,
            textvariable=self.step_var,
            font=("Segoe UI", 9),
            fg="#cbd5e0",
            bg="#12161f",
        ).pack(pady=(0, 8))

        style = ttk.Style(self.splash)
        style.theme_use("default")
        style.configure(
            "Splash.Horizontal.TProgressbar",
            troughcolor="#1e2533",
            background="#3182ce",
            bordercolor="#12161f",
            lightcolor="#3182ce",
            darkcolor="#3182ce",
        )

        self.progress = ttk.Progressbar(
            container,
            style="Splash.Horizontal.TProgressbar",
            orient=tk.HORIZONTAL,
            length=350,
            mode="determinate",
            maximum=100,
        )
        self.progress.pack(pady=(0, 12))

        self._steps = [
            (20, "Loading regex patterns & file filters..."),
            (50, "Preparing export & deduplication modules..."),
            (80, "Building desktop interface..."),
            (100, "Ready!"),
        ]
        self._step_index = 0
        self.splash.after(200, self._advance)

    def _advance(self) -> None:
        if self._step_index < len(self._steps):
            pct, msg = self._steps[self._step_index]
            self.progress["value"] = pct
            self.step_var.set(msg)
            self._step_index += 1
            self.splash.after(300, self._advance)
        else:
            self.splash.destroy()
            self.on_complete()


class ExportDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, matches: list[tuple[str, int, str]]) -> None:
        super().__init__(parent)
        self.title("Export Results — Email Searcher")
        self.geometry("430x295")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.matches = matches

        frame = ttk.Frame(self, padding=14)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame, text="Export Configuration", font=("Segoe UI", 11, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))

        # Export content mode
        mode_box = ttk.LabelFrame(frame, text="What to Export", padding=8)
        mode_box.pack(fill=tk.X, pady=(0, 8))

        self.mode_var = tk.StringVar(value="emails_only")
        ttk.Radiobutton(
            mode_box,
            text="Emails only (clean list)",
            variable=self.mode_var,
            value="emails_only",
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            mode_box,
            text="Full details (File path : Line -> Email)",
            variable=self.mode_var,
            value="full_details",
        ).pack(anchor=tk.W)

        # Separator selection
        sep_frame = ttk.Frame(frame)
        sep_frame.pack(fill=tk.X, pady=6)
        ttk.Label(sep_frame, text="Separator / Delimiter:", width=20).pack(side=tk.LEFT)
        self.sep_choice = tk.StringVar(value="New Line (\\n)")
        sep_combo = ttk.Combobox(
            sep_frame,
            textvariable=self.sep_choice,
            values=list(DELIMITERS.keys()) + ["Custom..."],
            state="readonly",
        )
        sep_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        sep_combo.bind("<<ComboboxSelected>>", self._on_sep_change)

        self.custom_frame = ttk.Frame(frame)
        ttk.Label(self.custom_frame, text="Custom Separator:", width=20).pack(side=tk.LEFT)
        self.custom_sep_var = tk.StringVar(value=" | ")
        ttk.Entry(self.custom_frame, textvariable=self.custom_sep_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

        # Deduplicate option
        self.dedup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Remove duplicate emails (case-insensitive)",
            variable=self.dedup_var,
        ).pack(anchor=tk.W, pady=(6, 12))

        # Action buttons
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(btn_row, text="Save File...", command=self._save).pack(
            side=tk.RIGHT, padx=(6, 0)
        )
        ttk.Button(btn_row, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def _on_sep_change(self, _event=None) -> None:
        if self.sep_choice.get() == "Custom...":
            self.custom_frame.pack(fill=tk.X, pady=(0, 6), before=self.children["!frame"].winfo_children()[4])
        else:
            self.custom_frame.pack_forget()

    def _get_separator(self) -> str:
        choice = self.sep_choice.get()
        if choice == "Custom...":
            raw = self.custom_sep_var.get()
            return raw.replace("\\n", "\n").replace("\\t", "\t")
        return DELIMITERS[choice]

    def _save(self) -> None:
        save_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".txt",
            initialfile="extracted_emails.txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )
        if not save_path:
            return

        emails_only = self.mode_var.get() == "emails_only"
        dedup = self.dedup_var.get()
        separator = self._get_separator()

        seen: set[str] = set()
        records: list[str] = []

        for filepath, line_num, email in self.matches:
            key = email.lower()
            if dedup:
                if key in seen:
                    continue
                seen.add(key)

            if emails_only:
                records.append(email)
            else:
                records.append(f"{filepath}:{line_num} -> {email}")

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(separator.join(records))
                if records and separator != "\n":
                    f.write("\n")
            messagebox.showinfo(
                "Export Complete",
                f"Exported {len(records)} item(s) to:\n{save_path}",
                parent=self,
            )
            self.destroy()
        except OSError as exc:
            messagebox.showerror(
                "Export Failed", f"Could not save file:\n{exc}", parent=self
            )


class EmailSearcherApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Email Searcher v0.0.2 — by AntiCrypto")
        self.root.geometry("860x610")
        self.root.minsize(720, 480)

        self.stop_event = threading.Event()
        self.worker_thread: threading.Thread | None = None
        self.matches: list[tuple[str, int, str]] = []
        self.seen_emails: set[str] = set()

        self._build_ui()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(
            header_frame,
            text="Email Searcher v0.0.2",
            font=("Segoe UI", 15, "bold"),
        ).pack(side=tk.LEFT)
        ttk.Label(
            header_frame,
            text="by AntiCrypto",
            font=("Segoe UI", 10, "italic"),
        ).pack(side=tk.LEFT, padx=(8, 0), pady=(5, 0))

        # Target directory row
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=4)
        ttk.Label(dir_frame, text="Scan Folder:", width=14).pack(side=tk.LEFT)
        self.dir_var = tk.StringVar(value=os.path.expanduser("~"))
        ttk.Entry(dir_frame, textvariable=self.dir_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)
        )
        ttk.Button(dir_frame, text="Browse...", command=self._browse_folder).pack(
            side=tk.LEFT
        )

        # Search query row
        query_frame = ttk.Frame(main_frame)
        query_frame.pack(fill=tk.X, pady=4)
        ttk.Label(query_frame, text="Email / Query:", width=14).pack(side=tk.LEFT)
        self.query_var = tk.StringVar()
        query_entry = ttk.Entry(query_frame, textvariable=self.query_var)
        query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        query_entry.bind("<Return>", lambda _e: self.start_scan())
        ttk.Label(
            query_frame,
            text="(blank = all emails; or type address / @domain)",
            font=("Segoe UI", 8),
        ).pack(side=tk.LEFT)

        # Extensions row
        ext_frame = ttk.Frame(main_frame)
        ext_frame.pack(fill=tk.X, pady=4)
        ttk.Label(ext_frame, text="Extensions:", width=14).pack(side=tk.LEFT)
        self.ext_var = tk.StringVar(value=", ".join(sorted(DEFAULT_EXTENSIONS)))
        ttk.Entry(ext_frame, textvariable=self.ext_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

        # Checkboxes row
        opts_frame = ttk.Frame(main_frame)
        opts_frame.pack(fill=tk.X, pady=4)
        ttk.Label(opts_frame, text="Options:", width=14).pack(side=tk.LEFT)

        self.dedup_live_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opts_frame,
            text="Remove duplicate emails",
            variable=self.dedup_live_var,
            command=self._refresh_display,
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.case_sensitive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opts_frame, text="Case sensitive", variable=self.case_sensitive_var
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.skip_sys_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opts_frame, text="Skip system/cache folders", variable=self.skip_sys_var
        ).pack(side=tk.LEFT)

        # Action buttons row
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(6, 8))
        self.start_btn = ttk.Button(btn_frame, text="Start Scan", command=self.start_scan)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.stop_btn = ttk.Button(
            btn_frame, text="Stop", command=self.stop_scan, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.export_btn = ttk.Button(
            btn_frame,
            text="Export Options...",
            command=self.open_export_dialog,
            state=tk.DISABLED,
        )
        self.export_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.dedup_btn = ttk.Button(
            btn_frame,
            text="Deduplicate Now",
            command=self.deduplicate_matches,
            state=tk.DISABLED,
        )
        self.dedup_btn.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_frame, text="Clear", command=self.clear_results).pack(side=tk.LEFT)

        # Progress & status
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(0, 4))

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(main_frame, textvariable=self.status_var, font=("Segoe UI", 9)).pack(
            fill=tk.X, pady=(0, 6)
        )

        # Results output area
        self.output = scrolledtext.ScrolledText(
            main_frame, wrap=tk.NONE, font=("Consolas", 9), state=tk.DISABLED
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        h_scroll = ttk.Scrollbar(
            self.output, orient=tk.HORIZONTAL, command=self.output.xview
        )
        self.output.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    def _browse_folder(self) -> None:
        chosen = filedialog.askdirectory(
            initialdir=self.dir_var.get() or os.path.expanduser("~")
        )
        if chosen:
            self.dir_var.set(chosen)

    def _parse_extensions(self) -> set[str]:
        raw = self.ext_var.get().strip()
        if not raw:
            return set(DEFAULT_EXTENSIONS)
        exts = set()
        for part in raw.split(","):
            ext = part.strip().lower()
            if not ext:
                continue
            if not ext.startswith("."):
                ext = "." + ext
            exts.add(ext)
        return exts

    def _append_output(self, text: str) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def _refresh_display(self) -> None:
        if not self.matches:
            return
        dedup = self.dedup_live_var.get()
        seen: set[str] = set()
        lines: list[str] = []

        for filepath, line_num, email in self.matches:
            if dedup:
                key = email.lower()
                if key in seen:
                    continue
                seen.add(key)
            lines.append(f"[{filepath}:{line_num}] {email}")

        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        if lines:
            self.output.insert(tk.END, "\n".join(lines) + "\n")
        self.output.configure(state=tk.DISABLED)

    def deduplicate_matches(self) -> None:
        if not self.matches:
            return
        before = len(self.matches)
        seen: set[str] = set()
        unique_matches: list[tuple[str, int, str]] = []
        for item in self.matches:
            key = item[2].lower()
            if key not in seen:
                seen.add(key)
                unique_matches.append(item)

        self.matches = unique_matches
        self.seen_emails = seen
        self.dedup_live_var.set(True)
        self._refresh_display()
        removed = before - len(self.matches)
        self.status_var.set(
            f"Removed {removed} duplicate(s). {len(self.matches)} unique email(s) remaining."
        )

    def clear_results(self) -> None:
        self.matches.clear()
        self.seen_emails.clear()
        self.export_btn.configure(state=tk.DISABLED)
        self.dedup_btn.configure(state=tk.DISABLED)
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.configure(state=tk.DISABLED)
        self.status_var.set("Cleared.")

    def start_scan(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            return

        root_dir = self.dir_var.get().strip()
        if not root_dir or not os.path.isdir(root_dir):
            messagebox.showerror("Invalid Folder", "Please select a valid folder to scan.")
            return

        query = self.query_var.get().strip()
        extensions = self._parse_extensions()
        case_sensitive = self.case_sensitive_var.get()
        skip_sys = self.skip_sys_var.get()
        dedup_live = self.dedup_live_var.get()

        self.clear_results()
        self.stop_event.clear()
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.progress.start(12)
        self.status_var.set(f"Scanning {root_dir}...")

        self.worker_thread = threading.Thread(
            target=self._scan_worker,
            args=(root_dir, query, extensions, case_sensitive, skip_sys, dedup_live),
            daemon=True,
        )
        self.worker_thread.start()

    def stop_scan(self) -> None:
        self.stop_event.set()
        self.status_var.set("Stopping scan...")

    def _matches_query(self, email: str, query: str, case_sensitive: bool) -> bool:
        if not query:
            return True
        if case_sensitive:
            return query in email
        return query.lower() in email.lower()

    def _scan_worker(
        self,
        root_dir: str,
        query: str,
        extensions: set[str],
        case_sensitive: bool,
        skip_sys: bool,
        dedup_live: bool,
    ) -> None:
        files_scanned = 0
        files_matched = 0
        skip_lower = {d.lower() for d in SKIP_DIRS}

        try:
            for current_root, dirnames, filenames in os.walk(root_dir):
                if self.stop_event.is_set():
                    break

                if skip_sys:
                    dirnames[:] = [
                        d for d in dirnames if d.lower() not in skip_lower
                    ]

                for filename in filenames:
                    if self.stop_event.is_set():
                        break

                    _, ext = os.path.splitext(filename)
                    if ext.lower() not in extensions:
                        continue

                    filepath = os.path.join(current_root, filename)
                    files_scanned += 1

                    if files_scanned % 25 == 0:
                        self.root.after(
                            0,
                            self.status_var.set,
                            f"Scanned {files_scanned} files | Found {len(self.matches)} matches...",
                        )

                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            file_has_match = False
                            for line_num, line in enumerate(f, start=1):
                                if self.stop_event.is_set():
                                    break
                                for match in EMAIL_REGEX.findall(line):
                                    if not self._matches_query(match, query, case_sensitive):
                                        continue

                                    key = match.lower()
                                    if dedup_live and key in self.seen_emails:
                                        continue

                                    self.seen_emails.add(key)
                                    self.matches.append((filepath, line_num, match))
                                    file_has_match = True
                                    line_out = f"[{filepath}:{line_num}] {match}"
                                    self.root.after(0, self._append_output, line_out)
                            if file_has_match:
                                files_matched += 1
                    except OSError:
                        continue
        finally:
            stopped = self.stop_event.is_set()
            summary = (
                f"{'Scan stopped' if stopped else 'Scan complete'}: "
                f"{len(self.matches)} email match(es) across {files_matched}/{files_scanned} scanned files."
            )
            self.root.after(0, self._finish_scan, summary)

    def _finish_scan(self, summary: str) -> None:
        self.progress.stop()
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        if self.matches:
            self.export_btn.configure(state=tk.NORMAL)
            self.dedup_btn.configure(state=tk.NORMAL)
        self.status_var.set(summary)

    def open_export_dialog(self) -> None:
        if not self.matches:
            return
        ExportDialog(self.root, self.matches)


def main() -> None:
    root = tk.Tk()
    root.withdraw()

    def launch_main() -> None:
        EmailSearcherApp(root)
        root.deiconify()

    SplashScreen(root, on_complete=launch_main)
    root.mainloop()


if __name__ == "__main__":
    main()