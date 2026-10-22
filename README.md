# MenuMate — Restaurant Menu Assistant

A student-friendly RAG-style demo using Python, ChromaDB, and `all-MiniLM-L6-v2`.

## Features
- Natural-language menu search with sentence embeddings.
- ChromaDB vector retrieval.
- Structured vegetarian and budget filters.
- Deterministic price/quantity totals.
- Allergy handling that fails cautiously when data is unverified.
- Streamlit user interface.
- Optional menu API adapter.

## Run locally
Use Python 3.10 or 3.11 recommended.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate

pip install -r requirements.txt
streamlit run app.py
```

The first run downloads the `all-MiniLM-L6-v2` model. Internet access is needed for that initial download.

## Important allergy limitation
The included menu is fictional demonstration data. All entries deliberately have `allergen_verified: false`, so the app will not present any of them as allergy-safe. Replace this file with official restaurant-provided menu and allergen information before using allergy recommendations in real life. Cross-contact can still occur even when an allergen is not listed.

## Real menu API
`menu_api.py` is an adapter template, not a connection to a specific provider. Set `MENU_API_URL` and optionally `MENU_API_KEY`, then adapt the mapping to the provider's documented response. Only treat allergen data as verified when the source explicitly supports that status.

## Project architecture
1. `menu_data.py`: local sample data.
2. `assistant.py`: embeddings, ChromaDB retrieval, filters, allergy checks, output.
3. `filters.py`: reusable structured filters.
4. `calculator.py`: bill calculation.
5. `menu_api.py`: optional API adapter.
6. `app.py`: Streamlit interface.

## Limitations
- Sample prices and ingredients are fictional.
- Semantic retrieval is a candidate-finding step, not a substitute for exact filtering.
- The demo returns up to six retrieved matches; for a production app, use metadata filters / query parsing that enforce all constraints across the full menu.
- This is a local demo, not a deployed website.
