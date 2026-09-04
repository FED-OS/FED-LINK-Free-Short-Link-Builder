# Copying

This file is the copy-policy statement for the FED-LINk repository. The
license itself lives in [`LICENSE`](LICENSE) (MIT). If you are reading
this to decide what you may do with this project, this page is the plain-
English summary — [`LICENSE`](LICENSE) is the legally binding text, and
[`NOTICE.md`](NOTICE.md) lists third-party notices that may apply to
specific files.

## The short version

MIT license: you may copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of FED-LINk, free of charge, for any purpose, as long
as you include the MIT copyright notice and permission notice in every
substantial copy of the software. It is licensed **as is**, with no
warranty of any kind.

## What that means in practice

- **Fork it, deploy it, sell hosting built on it.** Nothing in this
  repository restricts commercial use.
- **Keep the notice.** Any substantial copy of the code keeps the MIT
  header/notice (see [`LICENSE`](LICENSE) for the exact text).
- **Your links file is yours.** `configs/links.json` and generated
  `output/` content — your slugs and destinations — are your data, not
  part of the licensed code.
- **Rebranding is allowed.** The templates and CSS are generic; swap
  branding to your heart's content.
- **No trademark grant.** "FED-LINk" and "fedpromptly" branding appear in
  defaults and docs. The MIT grant covers code, not a license to imply
  endorsement; rename your fork.

## How to apply the license to your fork

1. Replace the `Copyright (c) 2026 fedpromptly` line in `LICENSE` with your
   own name/organization and year — MIT requires attribution, not
   identity.
2. Update the repo name, `README.md` badge lines, and the
   `--site-domain`/`--home-url` defaults if you changed them in `src/`.
3. Keep third-party notices accurate: if you add a dependency, add its
   notice to [`NOTICE.md`](NOTICE.md).

## Files that are not code

| File | Status |
|---|---|
| `LICENSE` | the MIT license text — do not remove |
| `NOTICE.md` | third-party notices — keep accurate when adding deps |
| `configs/links.json` | user data (your slugs) — yours entirely |
| `output/`, `links.zip` | generated artifacts — yours entirely |
| `docs/images/*`, `assets/*` | project graphics, MIT-licensed with the repo |

## Related pages

- [`LICENSE`](LICENSE) — the license itself
- [`NOTICE.md`](NOTICE.md) — third-party notices
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how contributions are licensed
  (MIT, and by submitting you agree to that)
- [`SECURITY.md`](SECURITY.md) — how to report issues responsibly
