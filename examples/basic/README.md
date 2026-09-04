# Basic example

The smallest possible FED-LINk configuration: a JSON object mapping each
short word to its destination URL.

```json
{
  "links": {
    "hello": "https://example.github.io/hello-world",
    "cv": "https://example.github.io/cv.pdf"
  }
}
```

## Build it

From the repository root:

```bash
python -m src.main build examples/basic/links.json --output output --zip links.zip
```

## What you get

| Short link | Redirects to |
|---|---|
| `https://link.fedpromptly.com/hello` | `https://example.github.io/hello-world` |
| `https://link.fedpromptly.com/cv` | `https://example.github.io/cv.pdf` |

Upload `links.zip` to the InfinityFree `htdocs` folder and both links are
live. See the main README for the full deployment walkthrough.
