# Streamlit dashboard example

A browser UI for managing the short links in `configs/links.json`: add,
edit and delete links with live validation, preview the generated
`.htaccess`, and build `links.zip` with one click.

## Install

```bash
pip install -r examples/streamlit_dashboard/requirements.txt
```

## Run

From the repository root (important — the dashboard imports `src/`):

```bash
streamlit run examples/streamlit_dashboard/app.py
```

The dashboard opens at http://localhost:8501.

## What it can do

| Feature | How |
|---|---|
| Add a link | type the short word + URL, hit **Save link** |
| Delete a link | the **Delete** button next to each row |
| Validate | every change is checked with the same rules as the CLI |
| Preview `.htaccess` | the **.htaccess preview** tab |
| Build bundle | the **Generate links.zip** button at the bottom |

## What it deliberately does not do

It never uploads anything. Deployment to InfinityFree stays a manual,
explicit step (see the root README) so a stray click cannot publish
half-finished links.
