"""FED-LINk Streamlit dashboard: manage short links in a browser.

Run from the repository root:

    streamlit run examples/streamlit_dashboard/app.py

The dashboard loads configs/links.json, lets you add, edit and delete
links with live validation, previews the resulting .htaccess, and writes
the file back when you save. It never deploys anything — deployment stays
a separate, explicit step.
"""

import json
import os
import sys

import streamlit as st

# Make the project importable when launched from this folder
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.generator.folder_creator import FolderCreator  # noqa: E402
from src.parsers import load_links  # noqa: E402
from src.validators import validate_links  # noqa: E402

LINKS_PATH = os.path.join(ROOT, "configs", "links.json")

st.set_page_config(page_title="FED-LINk Dashboard", page_icon="🔗",
                   layout="centered")

st.title("FED-LINk — Short Link Dashboard")
st.caption("link.fedpromptly.com · bundle builder for InfinityFree")


def load_config() -> dict:
    """Load the links file, tolerating the wrapper keys FED-LINk accepts."""
    if not os.path.exists(LINKS_PATH):
        return {}
    with open(LINKS_PATH, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data.get("links"), dict):
        return data["links"]
    if isinstance(data.get("links"), list):
        return {entry["path"].lstrip("/"): entry["url"] for entry in data["links"]}
    return data  # plain {slug: url} mapping


def save_config(links: dict) -> None:
    payload = {
        "site": "link.fedpromptly.com",
        "home": "https://fedpromptly.com",
        "links": links,
    }
    with open(LINKS_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


if "links" not in st.session_state:
    st.session_state.links = load_config()

links: dict = st.session_state.links

# --------------------------------------------------------------------- #
# add / edit / delete
# --------------------------------------------------------------------- #
with st.form("add_link", clear_on_submit=True):
    st.subheader("Add or update a link")
    new_slug = st.text_input("Short word", placeholder="portfolio")
    new_url = st.text_input("Destination URL", placeholder="https://…")
    submitted = st.form_submit_button("Save link", type="primary")
    if submitted:
        try:
            validate_links([(new_slug, new_url)])
        except Exception as exc:  # noqa: BLE001 - surface message in UI
            st.error(str(exc))
        else:
            links[new_slug.strip().lower()] = new_url.strip()
            save_config(links)
            st.success(f"Saved /{new_slug.strip().lower()} → {new_url.strip()}")

if links:
    st.subheader(f"Current links ({len(links)})")
    for slug in sorted(links):
        col_link, col_delete = st.columns([4, 1])
        col_link.markdown(
            f"**[/{slug}](https://link.fedpromptly.com/{slug})**  \n"
            f"<span style='color:gray'>{links[slug]}</span>",
            unsafe_allow_html=True,
        )
        if col_delete.button("Delete", key=f"del-{slug}"):
            del links[slug]
            save_config(links)
            st.rerun()
else:
    st.info("No links yet — add your first one above.")

# --------------------------------------------------------------------- #
# validation + preview
# --------------------------------------------------------------------- #
st.divider()
st.subheader("Validation & preview")

try:
    validate_links(list(links.items()))
    st.success(f"All {len(links)} links are valid.")
    errors = None
except Exception as exc:  # noqa: BLE001
    st.error(f"Invalid configuration: {exc}")
    errors = str(exc)

if links and not errors:
    tab_htaccess, tab_list = st.tabs([".htaccess preview", "Link list"])
    with tab_htaccess:
        creator = FolderCreator(output_dir=os.path.join(ROOT, "output"))
        st.code(creator._render_htaccess(links), language="apache")  # noqa: SLF001
    with tab_list:
        st.table(
            [{"Short link": f"/{slug}", "Destination": url}
             for slug, url in sorted(links.items())]
        )

st.divider()
st.subheader("Build bundle")
if st.button("Generate links.zip", type="primary", disabled=bool(errors) or not links):
    with st.spinner("Building…"):
        creator = FolderCreator(output_dir=os.path.join(ROOT, "output"))
        creator.generate(list(links.items()))
        st.success("Done — links.zip is in the repository root and output/ "
                   "holds the unpacked bundle. Upload it to InfinityFree.")
