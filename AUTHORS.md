# Authors

The people who wrote FED-LINk, in the order the project recognizes them.
Format mirrors the Git `shortlog` convention so it can be regenerated:

```bash
git shortlog -sne
```

## Project author

- **fedpromptly** — project owner, architecture, and implementation.
  Contact: the repository's Issues/Discussions, or the contact short link
  `link.fedpromptly.com/contact`.

## Contributors

| Name | Contributions |
|---|---|
| fedpromptly | all of `src/`, the 19 CI workflows, the docs suite, configs, templates, and tests |

(As outside contributions land, add them here — name, what they did, and
a link. The list is human-curated; `git shortlog -sne` is the audit trail.)

## Credits

FED-LINk stands on widely-deployed open infrastructure; these projects and
documents shaped the design (full rationale in [`ADR.md`](ADR.md)):

- **Apache HTTP Server** — `mod_alias` `Redirect` and `.htaccess` behavior
  that the entire redirect bundle targets. https://httpd.apache.org/
- **RFC 9110** — HTTP semantics, the `301 Moved Permanently` definition.
  https://www.rfc-editor.org/rfc/rfc9110
- **GitHub Actions / GitHub Pages** — the build pipeline and free static
  mirror. https://docs.github.com/
- **PyYAML** — optional YAML config support (lazily imported, never
  required). https://pyyaml.org/
- **Tkinter / Kivy** — the desktop GUI and Android front ends.
  https://kivy.org/
- **PyInstaller / Buildozer** — desktop and Android packaging.
  https://pyinstaller.org/ · https://buildozer.io/
- **InfinityFree** — the free static hosting the live site runs on.
  https://infinityfree.com/

No third-party code is vendored into this repository; the generator core
is written from scratch against the standard library (ADR-0004). See
[`NOTICE.md`](NOTICE.md) for third-party notices and
[`COPYING.md`](COPYING.md) for the copy policy.

## Copyright

Copyright (c) 2026 fedpromptly. Released under the MIT license — see
[`LICENSE`](LICENSE).
