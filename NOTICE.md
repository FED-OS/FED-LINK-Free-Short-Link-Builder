# Notice

Third-party notices for the FED-LINk repository. The project's own code
is MIT-licensed (see [`LICENSE`](LICENSE)); this file records the outside
software it depends on, invokes, or targets, so deployments that must
audit dependencies have one place to look.

## Runtime dependencies

| Dependency | License | Where it appears | Required? |
|---|---|---|---|
| Python 3.10+ | PSF License | the generator itself (`src/`) | yes |
| PyYAML | MIT | `src/parsers/yaml_parser.py` (deferred import) | only for `.yaml` links files |

**The core generator uses only the Python standard library.** PyYAML is
imported lazily at the moment a `.yaml` file is parsed (ADR-0004); with
the default `configs/links.json`, nothing outside the stdlib is touched.

## Development / build-time dependencies

| Dependency | License | Where it appears | Required? |
|---|---|---|---|
| pytest | MIT | `tests/` | for running tests |
| ruff | MIT | lint hooks, `ci.yml`, pre-commit | for linting |
| pre-commit | MIT | `.pre-commit-config.yaml` | for git hooks |
| PyInstaller | GPL-with-exception | `pyinstaller.spec`, `build-desktop.yml` | for desktop binaries |
| Buildozer | MIT | `buildozer.spec`, `build-android.yml` | for Android APKs |
| Kivy | MIT | Android front end (`src/main.py` Kivy path) | for the Android app |
| Streamlit | Apache-2.0 | `examples/streamlit_dashboard/` | for the example dashboard |
| Matplotlib | Matplotlib license (BSD-style) | example tooling only | examples only |

PyInstaller note: PyInstaller is GPL with a special exception that allows
its output (your frozen app) to be under any license — the FED-LINk
desktop binaries remain MIT-licensed with the rest of the project; no
GPL obligation attaches to the frozen executables or to your generated
redirect bundles.

## Infrastructure targeted (not distributed)

These are services/software the project generates content *for*; none of
their code ships in this repository:

| Target | Role | Reference |
|---|---|---|
| Apache HTTP Server (`mod_alias`, `.htaccess`) | executes the generated `Redirect 301` rules on InfinityFree | https://httpd.apache.org/docs/ |
| InfinityFree hosting | live host of `link.fedpromptly.com` | https://infinityfree.com/ |
| GitHub Pages | automatic mirror of the bundle | https://docs.github.com/pages |
| IONOS DNS | `link` CNAME for `fedpromptly.com` | https://www.ionos.com/ |
| ko-fi.com | donation link target (`kofi` slug) | https://ko-fi.com/ |

## Trademarks

"FED-LINk" is a project name. "fedpromptly", "InfinityFree", "IONOS",
"GitHub", "Bitly", "Dub.co", "Kivy", "PyInstaller", "Buildozer",
"Streamlit", "Apache", and the ko-fi name/logo are trademarks of their
respective owners. Their appearance here is referential; no endorsement
is implied and no trademark rights are granted (see
[`COPYING.md`](COPYING.md)).

## No data collection

FED-LINk is a build-time generator: it runs offline, reads your links
file, and writes files. It makes no network requests, includes no
telemetry, and tracks nothing. The only network activity the repository
performs is what GitHub Actions does when CI runs, and what you do when
you upload the result. This is a recorded design property, not an
accident — see ADR-0001 and the FAQ privacy stance.
