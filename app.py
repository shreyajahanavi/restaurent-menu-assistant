import streamlit as st
from menu_data import MENU
from assistant import RestaurantMenuAssistant

st.set_page_config(page_title="MenuMate | Restaurant Menu Assistant", page_icon="🍽️", layout="wide")

@st.cache_resource
def get_assistant():
    return RestaurantMenuAssistant(MENU)

assistant = get_assistant()

st.markdown("""
<style>
   
.stApp {
    background: #FBF8F3;
    color: #26352D;
}

[data-testid="stSidebar"] {
    background: #F1E8DC;
}

/* Make all normal text readable */
.stApp p,
.stApp label,
.stApp span,
.stApp li,
.stApp div {
    color: #26352D;
}

/* Headings */
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #243B32 !important;
}

/* Remove ugly text-selection colors */
::selection {
    background: #C5D9C8;
    color: #17271E;
}

/* Result cards */
.dish {
    background: #FFFFFF;
    border: 1px solid #E8DFD4;
    border-radius: 14px;
    padding: 1rem;
    margin: .5rem 0;
}

.price {
    color: #2F6548 !important;
    font-size: 1.25rem;
    font-weight: 750;
}

.small {
    color: #666B63 !important;
    font-size: .9rem;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🍽️ MenuMate</h1>
  <p>Your smart restaurant menu assistant — find dishes, stay within budget, and check ingredient information.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Find your meal")
    vegetarian_only = st.toggle("Vegetarian only", value=False)
    budget = st.number_input("Maximum budget (₹)", min_value=0, max_value=10000, value=500, step=50)
    allergy = st.selectbox("Allergy to check", ["None", "Peanuts", "Milk", "Wheat", "Soy", "Egg", "Sesame"])
    people = st.number_input("People / portions", min_value=1, max_value=20, value=1)
    st.caption("Allergy data in this demo is illustrative. Always confirm with the restaurant.")

left, right = st.columns([1.25, 1])
with left:
    st.subheader("Ask the assistant")
    query = st.text_input(
        "What are you looking for?",
        placeholder="e.g. vegetarian dishes under ₹300, or meals without peanuts",
        value=""
    )
    examples = st.columns(3)
    if examples[0].button("🥦 Vegetarian"):
        query = "Suggest vegetarian dishes"
    if examples[1].button("💸 Budget meal"):
        query = f"Suggest dishes under ₹{int(budget)}"
    if examples[2].button("⚠️ Allergy check"):
        query = f"Find dishes without {allergy.lower()}" if allergy != "None" else "Show allergen information"

    if st.button("Find dishes", type="primary", use_container_width=True):
        if not query.strip():
            query = "Suggest popular dishes"
        result = assistant.answer(
            query=query,
            vegetarian_only=vegetarian_only,
            budget=float(budget),
            allergy=None if allergy == "None" else allergy,
            portions=int(people),
        )
        st.session_state["result"] = result

with right:
    st.subheader("Quick facts")
    st.metric("Menu items", len(MENU))
    st.metric("Vegetarian options", sum(1 for d in MENU if d["vegetarian"]))
    st.info("The demo uses a local menu dataset. The API adapter can be connected to a real restaurant API.")

if "result" in st.session_state:
    result = st.session_state["result"]
    st.divider()
    st.subheader("Recommendations")
    if result["warnings"]:
        for warning in result["warnings"]:
            st.warning(warning)
    if not result["dishes"]:
        st.warning("No dishes matched every selected filter. Try increasing the budget or changing a filter.")
    else:
        for dish in result["dishes"]:
            allergens = ", ".join(dish["allergens"]) if dish["allergens"] else "None listed"
            st.markdown(f"""
            <div class="dish">
              <div style="display:flex;justify-content:space-between;gap:1rem;align-items:start">
                <div><strong>{dish['name']}</strong><br>
                <span class="small">{dish['category']} · {'Vegetarian' if dish['vegetarian'] else 'Non-vegetarian'}</span></div>
                <div class="price">₹{dish['price'] * int(people):.0f}</div>
              </div>
              <p>{dish['description']}</p>
              <span class="small">Listed allergens: {allergens}</span>
            </div>
            """, unsafe_allow_html=True)
    st.markdown(f"### Estimated total: ₹{result['total']:.2f}")
    st.caption(f"{int(people)} portion(s) per selected dish. Prices are sample data; taxes and service charges are not included.")
    if result["allergy_notes"]:
        st.subheader("Allergy information")
        for note in result["allergy_notes"]:
            st.warning(note)

with st.expander("Browse full sample menu"):
    st.dataframe(
        [{"Dish": d["name"], "Price (₹)": d["price"], "Vegetarian": d["vegetarian"],
          "Category": d["category"], "Allergens": ", ".join(d["allergens"]) or "None listed",
          "Allergen data verified": d["allergen_verified"]} for d in MENU],
        use_container_width=True,
        hide_index=True,
    )
