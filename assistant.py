import re
from typing import Optional
import chromadb
from sentence_transformers import SentenceTransformer

class RestaurantMenuAssistant:
    """Retrieval + structured filtering + deterministic total calculation."""

    def __init__(self, menu):
        self.menu = menu
        self.by_id = {item["id"]: item for item in menu}
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.Client()
        try:
            self.client.delete_collection("restaurant_menu")
        except Exception:
            pass
        self.collection = self.client.create_collection(
            name="restaurant_menu",
            metadata={"hnsw:space": "cosine"}
        )
        documents = [
            f"{d['name']}. {d['description']}. Category: {d['category']}. "
            f"{'Vegetarian' if d['vegetarian'] else 'Non-vegetarian'}. "
            f"Ingredients: {', '.join(d['ingredients'])}. Allergens: {', '.join(d['allergens'])}."
            for d in menu
        ]
        embeddings = self.embedder.encode(documents, normalize_embeddings=True).tolist()
        self.collection.add(
            ids=[d["id"] for d in menu],
            documents=documents,
            embeddings=embeddings,
            metadatas=[{
                "price": float(d["price"]),
                "vegetarian": bool(d["vegetarian"]),
                "category": d["category"],
                "allergen_verified": bool(d["allergen_verified"]),
            } for d in menu],
        )

    @staticmethod
    def _budget_from_query(query: str) -> Optional[float]:
        match = re.search(r"(?:under|below|within|budget(?:\s+of)?|₹|rs\.?\s*)(?:\s*₹?\s*)(\d+(?:\.\d+)?)", query.lower())
        return float(match.group(1)) if match else None

    def answer(self, query, vegetarian_only=False, budget=500, allergy=None, portions=1):
        query_lower = query.lower()
        query_embedding = self.embedder.encode([query], normalize_embeddings=True).tolist()[0]
        hits = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(12, len(self.menu)),
            include=["metadatas", "documents", "distances"],
        )
        ids = hits.get("ids", [[]])[0]
        retrieved = [self.by_id[item_id] for item_id in ids if item_id in self.by_id]

        # Hard constraints are applied after semantic retrieval. Budget is per dish.
        query_budget = self._budget_from_query(query)
        max_budget = query_budget if query_budget is not None else float(budget)
        wants_veg = vegetarian_only or any(x in query_lower for x in ["vegetarian", "veggie", "veg-only", "veg only"])
        candidates = [
            d for d in retrieved
            if d["price"] <= max_budget
            and (not wants_veg or d["vegetarian"])
        ]

        warnings = []
        allergy_notes = []
        if allergy:
            if not any(allergy.lower() in a.lower() for d in self.menu for a in d["allergens"]):
                warnings.append(f"No reliable allergen match for '{allergy}' exists in the sample menu. Ask the restaurant directly.")
            safe_candidates = []
            for d in candidates:
                if not d["allergen_verified"]:
                    allergy_notes.append(f"{d['name']}: allergen information is not verified; do not treat this dish as allergy-safe.")
                    continue
                if any(allergy.lower() in a.lower() for a in d["allergens"]):
                    allergy_notes.append(f"{d['name']}: listed as containing {allergy}. Excluded.")
                    continue
                if d.get("cross_contact_unknown", True):
                    allergy_notes.append(f"{d['name']}: the listed ingredients do not include {allergy}, but cross-contact is not confirmed. Verify with the restaurant.")
                safe_candidates.append(d)
            candidates = safe_candidates

        # Avoid duplicates and show the best matching menu results.
        seen, dishes = set(), []
        for d in candidates:
            if d["id"] not in seen:
                seen.add(d["id"])
                dishes.append(d)
        dishes = dishes[:6]
        total = sum(float(d["price"]) * int(portions) for d in dishes)

        if allergy and not dishes:
            warnings.append("No dishes can be recommended from the current data with sufficient confidence for this allergy.")
        return {
            "dishes": dishes,
            "total": total,
            "warnings": warnings,
            "allergy_notes": list(dict.fromkeys(allergy_notes)),
            "max_budget": max_budget,
            "retrieved_count": len(retrieved),
        }
