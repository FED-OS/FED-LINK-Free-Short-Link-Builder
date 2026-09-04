#!/usr/bin/env python3
"""FED-LINk application entrypoint: CLI first, desktop GUI as a fallback.

Command line (this is the interface the GitHub Actions use)::

    python -m src.main build configs/links.json --output output --zip links.zip
    python -m src.main build configs/links.json --dry-run
    python -m src.main validate configs/links.json --format json
    python -m src.main list configs/links.json
    python -m src.main check configs/links.json
    python -m src.main generate-htaccess configs/links.json

The links file is a positional argument (``build configs/links.json``);
there is no ``--links`` flag.

Version 1.1 adds four workflow features from the ROADMAP:

* ``check`` — probe every *deployed* short link with a live HEAD request
  and compare the redirect target against the links file
* ``--strict-case`` — reject mixed-case slugs instead of silently
  lower-casing them (the links file becomes the literal source of truth)
* ``--dry-run`` — preview exactly what a build would create, update,
  keep and remove, without writing a single file
* ``--format json`` — machine-readable output for ``validate``, ``list``
  and ``check`` (and for ``build --dry-run``), so scripts and CI jobs can
  consume the results directly

With no arguments the app starts a graphical front end: the Kivy UI on
Android (guarded import, ADR-0008), otherwise the Tkinter desktop window
used by the PyInstaller desktop builds; if no display is available it
prints the help text instead, so the same file works in CI and on a
laptop.
"""

import argparse
import json
import os
import sys

from src import __version__
from src.parsers import load_links
from src.parsers.json_parser import MalformedLinksFileError
from src.generator.folder_creator import FolderCreator
from src.generator.zip_packager import ZipPackager
from src.validators import (
    LinkValidationError,
    build_check_url,
    check_links,
    validate_links,
)
from src.utils.logger import get_logger, setup_logging

_LOG = get_logger("main")

_LINKS_DEFAULT = os.path.join("configs", "links.json")
_OUTPUT_DEFAULT = "output"
_ZIP_DEFAULT = "links.zip"

_FORMATS = ("text", "json")


def _fail(message: str, code: int = 2) -> int:
    print(f"error: {message}", file=sys.stderr)
    return code


def _resolve_htaccess_template(explicit: str | None) -> str | None:
    """Pick the .htaccess template: the explicit flag, else configs/."""
    if explicit is None and os.path.isfile(
            os.path.join("configs", ".htaccess.template")):
        return os.path.join("configs", ".htaccess.template")
    return explicit


# ---------------------------------------------------------------------- #
# commands
# ---------------------------------------------------------------------- #
def _print_plan(plan: dict, links_path: str, output_dir: str) -> None:
    """Human-readable rendering of a ``plan()`` result (``--dry-run``)."""
    print(f"Dry run for '{links_path}' -> '{output_dir}' (nothing was written)")
    groups: dict[str, list[str]] = {}
    for slug, action in plan["actions"].items():
        groups.setdefault(action, []).append(slug)
    for action in ("create", "update", "keep"):
        members = groups.get(action, [])
        if members:
            print(f"  {action} {len(members)}: {', '.join(members)}")
    if plan["stale"]:
        print(f"  stale {len(plan['stale'])} (removed on a real build): "
              f"{', '.join(plan['stale'])}")
    writes = [
        name for name, flag in (
            ("404.html", plan["write_404"]),
            (".htaccess", plan["write_htaccess"]),
            ("links.json", plan["write_manifest"]),
        ) if flag
    ]
    if writes:
        print(f"  support files to rewrite: {', '.join(writes)}")
    else:
        print("  support files already current")
    if not plan["changes"]:
        print("Result: output already up to date — a real build would "
              "change nothing")
    else:
        print("Result: a real build would apply the changes above")


def cmd_build(args: argparse.Namespace) -> int:
    try:
        pairs = load_links(args.links)
    except (MalformedLinksFileError, FileNotFoundError) as exc:
        return _fail(str(exc))
    try:
        mapping = validate_links(pairs, allow_private=args.allow_private,
                                 strict_case=args.strict_case)
    except LinkValidationError as exc:
        return _fail(str(exc))

    creator = FolderCreator(
        output_dir=args.output,
        template_path=args.page_template,
        htaccess_template=_resolve_htaccess_template(args.htaccess_template),
        site_domain=args.site_domain,
        home_url=args.home_url,
    )

    if args.dry_run:
        plan = creator.plan(mapping.items())
        if args.format == "json":
            print(json.dumps(plan, indent=2))
        else:
            _print_plan(plan, args.links, args.output)
        return 0

    try:
        written = creator.generate(mapping.items(), clean=not args.no_clean)
    except OSError as exc:
        return _fail(f"cannot write output: {exc}")

    print(f"Generated {len(written)} redirect page(s) into '{args.output}'")

    if not args.no_zip:
        packager = ZipPackager(source_dir=args.output, zip_path=args.zip)
        try:
            zip_path, count = packager.package(clean_first=True)
        except OSError as exc:
            return _fail(f"cannot write zip: {exc}")
        print(f"Packaged {count} file(s) into '{zip_path}'")

    for relative, url in written.items():
        print(f"  {relative}  ->  {url}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        pairs = load_links(args.links)
        mapping = validate_links(pairs, allow_private=args.allow_private,
                                 strict_case=args.strict_case)
    except (MalformedLinksFileError, LinkValidationError,
            FileNotFoundError) as exc:
        if args.format == "json":
            print(json.dumps({"ok": False, "error": str(exc)}))
        else:
            print(f"invalid: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps({"ok": True, "count": len(mapping),
                          "links": mapping}, indent=2))
    else:
        print(f"OK: {len(mapping)} link(s) valid")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    try:
        pairs = load_links(args.links)
        mapping = validate_links(pairs, allow_private=args.allow_private,
                                 strict_case=args.strict_case)
    except (MalformedLinksFileError, LinkValidationError,
            FileNotFoundError) as exc:
        return _fail(str(exc))
    if args.format == "json":
        rows = [
            {
                "slug": slug,
                "short_url": build_check_url(args.site_domain, slug),
                "url": url,
            }
            for slug, url in mapping.items()
        ]
        print(json.dumps(rows, indent=2))
        return 0
    for slug, url in mapping.items():
        print(f"https://{args.site_domain}/{slug}  ->  {url}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """Probe the deployed short links and compare them to the links file."""
    try:
        pairs = load_links(args.links)
    except (MalformedLinksFileError, FileNotFoundError) as exc:
        return _fail(str(exc))
    try:
        results = check_links(pairs,
                              site_domain=args.site_domain,
                              timeout=args.timeout,
                              allow_private=args.allow_private,
                              strict_case=args.strict_case)
    except LinkValidationError as exc:
        return _fail(str(exc))

    if args.format == "json":
        payload = {
            "site": args.site_domain,
            "count": len(results),
            "ok": sum(1 for result in results if result.ok),
            "results": [result.as_dict() for result in results],
        }
        print(json.dumps(payload, indent=2))
    else:
        for result in results:
            print(f"{result.slug:<20} {result.status:<13} {result.detail}")
        ok_count = sum(1 for result in results if result.ok)
        print()
        print(f"{ok_count} of {len(results)} short links OK")
    return 0 if all(result.ok for result in results) else 1


def cmd_generate_htaccess(args: argparse.Namespace) -> int:
    try:
        pairs = load_links(args.links)
        mapping = validate_links(pairs, allow_private=args.allow_private,
                                 strict_case=args.strict_case)
    except (MalformedLinksFileError, LinkValidationError,
            FileNotFoundError) as exc:
        return _fail(str(exc))

    creator = FolderCreator(
        output_dir=_OUTPUT_DEFAULT,
        htaccess_template=_resolve_htaccess_template(args.htaccess_template),
        site_domain=args.site_domain,
        home_url=args.home_url,
    )
    # render against a throwaway directory without touching output/
    content = creator._render_htaccess(mapping)  # noqa: SLF001 - internal use
    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        print(f"Wrote {len(mapping)} redirect rule(s) to {args.output_file}")
    else:
        sys.stdout.write(content)
    return 0


# ---------------------------------------------------------------------- #
# desktop GUI (Tkinter; also the PyInstaller entrypoint)
# ---------------------------------------------------------------------- #
def run_kivy() -> int:
    """Start the Kivy front end (Android via Buildozer, ADR-0008).

    The import is guarded so a machine without Kivy installed (every
    desktop/CI host) never hits it: the caller only invokes this when
    the ``kivy`` module is importable. On Android ``android`` is present
    in build artifacts, so the UI runs there.
    """
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput

    class FedLinkKivyApp(App):
        title = "FED-LINk"

        def build(self):
            root = BoxLayout(orientation="vertical", padding=12, spacing=8)
            root.add_widget(Label(text="Links file (JSON / YAML / CSV):"))
            self.path_input = TextInput(text=_LINKS_DEFAULT,
                                        multiline=False, size_hint_y=None,
                                        height=40)
            root.add_widget(self.path_input)
            self.status = Label(text="Ready.")
            root.add_widget(self.status)
            buttons = BoxLayout(orientation="horizontal",
                                size_hint_y=None, height=48, spacing=8)
            buttons.add_widget(Button(text="Validate",
                                      on_release=self._validate))
            buttons.add_widget(Button(text="Build",
                                      on_release=self._build))
            root.add_widget(buttons)
            self.log_label = Label(text="", valign="top")
            root.add_widget(self.log_label)
            return root

        def _set_status(self, message: str) -> None:
            self.status.text = message
            self.log_label.text = message

        def _validate(self, _button) -> None:
            try:
                pairs = load_links(self.path_input.text)
                validate_links(pairs)
                self._set_status(f"OK: {len(pairs)} link(s) valid")
            except Exception as exc:  # noqa: BLE001 - UI catches all
                self._set_status(f"error: {exc}")

        def _build(self, _button) -> None:
            try:
                pairs = load_links(self.path_input.text)
                mapping = validate_links(pairs)
                creator = FolderCreator()
                written = creator.generate(mapping.items())
                packager = ZipPackager()
                zip_path, count = packager.package(clean_first=True)
                self._set_status(
                    f"Generated {len(written)} page(s); packaged "
                    f"{count} file(s) into {zip_path}")
            except Exception as exc:  # noqa: BLE001 - UI catches all
                self._set_status(f"error: {exc}")

    FedLinkKivyApp().run()
    return 0


def run_gui() -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, scrolledtext
    except ImportError:
        print("No arguments given and Tkinter is unavailable.")
        print("Pass --help to see the available commands.")
        return 1

    class FedLinkApp(tk.Tk):
        def __init__(self) -> None:
            super().__init__()
            self.title("FED-LINk — Short Link Builder")
            self.geometry("640x480")
            self.minsize(560, 420)
            self._build_ui()

        def _build_ui(self) -> None:
            frame = tk.Frame(self, padx=12, pady=12)
            frame.pack(fill="both", expand=True)

            tk.Label(frame, text="Links file (JSON / YAML / CSV):").grid(
                row=0, column=0, sticky="w")
            self.path_var = tk.StringVar(value=_LINKS_DEFAULT)
            tk.Entry(frame, textvariable=self.path_var).grid(
                row=1, column=0, sticky="ew", padx=(0, 6))
            tk.Button(frame, text="Browse…", command=self._browse).grid(
                row=1, column=1)

            button_row = tk.Frame(frame)
            button_row.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)
            tk.Button(button_row, text="Validate", command=self._validate).pack(
                side="left", padx=(0, 6))
            tk.Button(button_row, text="Build", command=self._build).pack(
                side="left")

            self.log_box = scrolledtext.ScrolledText(frame, height=18, state="disabled")
            self.log_box.grid(row=3, column=0, columnspan=2, sticky="nsew")
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(3, weight=1)

        def _log(self, message: str) -> None:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", message.rstrip() + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        def _browse(self) -> None:
            chosen = filedialog.askopenfilename(
                title="Choose a links file",
                filetypes=[("Links files", "*.json *.yaml *.yml *.csv"),
                           ("All files", "*.*")],
            )
            if chosen:
                self.path_var.set(chosen)

        def _run(self, handler) -> None:
            self._log(f"--- {self.path_var.get()} ---")
            try:
                handler(self.path_var.get())
            except Exception as exc:  # noqa: BLE001 - GUI catches all
                messagebox.showerror("FED-LINk", str(exc))
                self._log(f"error: {exc}")

        def _validate(self) -> None:
            def handler(path: str) -> None:
                pairs = load_links(path)
                validate_links(pairs)
                self._log(f"OK: {len(pairs)} link(s) valid")
            self._run(handler)

        def _build(self) -> None:
            def handler(path: str) -> None:
                pairs = load_links(path)
                mapping = validate_links(pairs)
                creator = FolderCreator()
                written = creator.generate(mapping.items())
                packager = ZipPackager()
                zip_path, count = packager.package(clean_first=True)
                self._log(f"Generated {len(written)} page(s); packaged "
                          f"{count} file(s) into {zip_path}")
            self._run(handler)

    FedLinkApp().mainloop()
    return 0


# ---------------------------------------------------------------------- #
# argument parsing
# ---------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fedlink",
        description="Build InfinityFree short-link bundles from a links file.",
    )
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    def add_links_argument(target: argparse.ArgumentParser) -> None:
        target.add_argument("links", nargs="?", default=_LINKS_DEFAULT,
                            help=f"links file (default: {_LINKS_DEFAULT})")

    def add_format(target: argparse.ArgumentParser) -> None:
        target.add_argument("--format", choices=_FORMATS, default="text",
                            help="text summary or machine-readable JSON "
                                 "(default: text)")

    def add_common(target: argparse.ArgumentParser) -> None:
        add_links_argument(target)
        target.add_argument("--site-domain", default="link.fedpromptly.com",
                            help="public domain of the redirect site")
        target.add_argument("--home-url", default="https://fedpromptly.com",
                            help="fallback destination for unknown links")
        target.add_argument("--allow-private", action="store_true",
                            help="allow localhost/private URLs (testing only)")
        target.add_argument("--strict-case", action="store_true",
                            help="reject mixed-case slugs instead of "
                                 "lower-casing them")

    build_cmd = subparsers.add_parser(
        "build", help="generate redirect folders, .htaccess and links.zip")
    add_common(build_cmd)
    build_cmd.add_argument("--output", default=_OUTPUT_DEFAULT,
                           help=f"output directory (default: {_OUTPUT_DEFAULT})")
    build_cmd.add_argument("--zip", default=_ZIP_DEFAULT,
                           help=f"zip file to create (default: {_ZIP_DEFAULT})")
    build_cmd.add_argument("--no-zip", action="store_true",
                           help="skip creating the zip archive")
    build_cmd.add_argument("--no-clean", action="store_true",
                           help="keep existing files in the output directory")
    build_cmd.add_argument("--page-template", default=None,
                           help="custom redirect page template")
    build_cmd.add_argument("--htaccess-template", default=None,
                           help="custom .htaccess template")
    build_cmd.add_argument("--dry-run", action="store_true",
                           help="preview what the build would write, then "
                                "exit without touching the output directory")
    add_format(build_cmd)
    build_cmd.set_defaults(func=cmd_build)

    validate_cmd = subparsers.add_parser(
        "validate", help="check a links file without building anything")
    add_common(validate_cmd)
    add_format(validate_cmd)
    validate_cmd.set_defaults(func=cmd_validate)

    list_cmd = subparsers.add_parser(
        "list", help="print every short URL with its destination")
    add_common(list_cmd)
    add_format(list_cmd)
    list_cmd.set_defaults(func=cmd_list)

    check_cmd = subparsers.add_parser(
        "check",
        help="probe every deployed short link with a live HEAD request "
             "and compare it to the links file")
    add_common(check_cmd)
    check_cmd.add_argument("--timeout", type=float, default=10.0,
                           help="seconds to wait per HEAD request "
                                "(default: 10)")
    add_format(check_cmd)
    check_cmd.set_defaults(func=cmd_check)

    htaccess_cmd = subparsers.add_parser(
        "generate-htaccess",
        help="print (or write) the .htaccess redirect rules")
    add_common(htaccess_cmd)
    htaccess_cmd.add_argument("--output-file", default=None,
                              help="write rules to this file instead of stdout")
    htaccess_cmd.set_defaults(func=cmd_generate_htaccess)

    return parser


def main(argv: list[str] | None = None) -> int:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        try:
            import kivy  # noqa: F401 - presence check for Android
            _HAS_KIVY = True
        except ImportError:
            _HAS_KIVY = False
        if _HAS_KIVY:
            return run_kivy()
        if sys.stdout.isatty() or os.environ.get("DISPLAY"):
            return run_gui()
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
