"""
MSP Lead Scraper — Streamlit Web App
=====================================
Run with:
    streamlit run app.py

Make sure scraper.py is in the same folder.
"""

import streamlit as st
import pandas as pd
import time
import os
from io import StringIO
import scraper as scraper_module
from scraper import run_scraper, search_google_places, parse_place, scrape_website, enrich_email_hunter, score_lead
from urllib.parse import urlparse

# ── Vertical Recommender ───────────────────────────────────────────────────────

# All verticals we test + why MSPs love them
VERTICALS_META = {
    "dental office":          {"icon": "🦷", "reason": "HIPAA compliance, no IT staff, high revenue"},
    "law firm":               {"icon": "⚖️", "reason": "Sensitive data, strict uptime, no IT dept"},
    "accounting firm":        {"icon": "📊", "reason": "Compliance needs, tax season crunch"},
    "medical clinic":         {"icon": "🏥", "reason": "HIPAA, EMR systems, always need IT"},
    "real estate agency":     {"icon": "🏠", "reason": "Cloud-heavy, distributed teams"},
    "veterinary clinic":      {"icon": "🐾", "reason": "Practice mgmt software, small teams"},
    "insurance agency":       {"icon": "📋", "reason": "Data-sensitive, compliance-driven"},
    "financial advisor":      {"icon": "💼", "reason": "SEC compliance, high trust requirements"},
    "construction company":   {"icon": "🏗️", "reason": "Field + office IT, project mgmt tools"},
    "chiropractic office":    {"icon": "🩺", "reason": "HIPAA, small staff, EHR systems"},
    "optometry clinic":       {"icon": "👁️", "reason": "HIPAA, specialized software"},
    "physical therapy clinic":{"icon": "💪", "reason": "HIPAA, billing software, no IT"},
    "architecture firm":      {"icon": "📐", "reason": "CAD/BIM software, large file mgmt"},
    "marketing agency":       {"icon": "📣", "reason": "SaaS-heavy, remote teams, fast growth"},
}

def analyze_verticals(location: str, top_n: int = 5) -> pd.DataFrame:
    """
    For each vertical, do a quick Google Maps search and score:
      - Volume       (how many businesses found)
      - Avg rating   (healthy businesses = better clients)
      - MSP fit      (static score based on known industry traits)
    Returns a ranked DataFrame of recommendations.
    """
    MSP_FIT_SCORES = {
        "dental office": 95,         "medical clinic": 93,
        "chiropractic office": 90,   "optometry clinic": 88,
        "physical therapy clinic": 87, "law firm": 92,
        "accounting firm": 89,       "financial advisor": 85,
        "insurance agency": 83,      "veterinary clinic": 80,
        "real estate agency": 78,    "construction company": 75,
        "architecture firm": 72,     "marketing agency": 70,
    }

    rows = []
    for vertical, meta in VERTICALS_META.items():
        places = search_google_places(vertical, location, num_results=5)
        volume = len(places)

        ratings = []
        for p in places:
            try:
                ratings.append(float(p.get("rating", 0)))
            except (TypeError, ValueError):
                pass
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

        msp_fit    = MSP_FIT_SCORES.get(vertical, 70)
        # Composite: 40% MSP fit, 35% volume (normalized to 20 max), 25% rating
        volume_norm = min(volume / 5 * 100, 100)
        rating_norm = (avg_rating / 5) * 100
        composite   = round(0.40 * msp_fit + 0.35 * volume_norm + 0.25 * rating_norm)

        rows.append({
            "icon":        meta["icon"],
            "vertical":    vertical.title(),
            "volume":      volume,
            "avg_rating":  avg_rating,
            "msp_fit":     msp_fit,
            "score":       composite,
            "reason":      meta["reason"],
        })

        time.sleep(0.5)  # be polite to the API

    df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    df.index += 1
    return df.head(top_n)

# ── Page Config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="MSP Lead Scraper",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border-left: 4px solid #4f46e5;
    }
    .score-high   { color: #16a34a; font-weight: 700; }
    .score-mid    { color: #d97706; font-weight: 700; }
    .score-low    { color: #dc2626; font-weight: 700; }
    .stDataFrame  { border-radius: 10px; }
    div[data-testid="stSidebarContent"] { background: #1a1a2e; }
    div[data-testid="stSidebarContent"] * { color: white !important; }
    div[data-testid="stSidebarContent"] .stSelectbox label,
    div[data-testid="stSidebarContent"] .stSlider label,
    div[data-testid="stSidebarContent"] .stTextInput label { color: #ccc !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎯 MSP Lead Scraper")
    st.markdown("---")

    st.markdown("### 🔑 API Keys")
    serper_key   = st.text_input("Serper Key (recommended)",  type="password",
                                 placeholder="2,500 free/mo — serper.dev")
    serpapi_key   = st.text_input("SerpAPI Key (alternative)", type="password",
                                 placeholder="100 free/mo — serpapi.com")
    hunter_key   = st.text_input("Hunter.io Key (optional)",  type="password",
                                 placeholder="25 free/mo — hunter.io")

    if serper_key:
        os.environ["SERPER_KEY"] = serper_key
        scraper_module.SERPER_KEY = serper_key
    if serpapi_key:
        os.environ["SERPAPI_KEY"] = serpapi_key
        scraper_module.SERPAPI_KEY = serpapi_key
    if hunter_key:
        os.environ["HUNTER_KEY"] = hunter_key
        scraper_module.HUNTER_KEY = hunter_key

    st.markdown("---")
    st.markdown("### 🔍 Search Settings")

    CATEGORY_PRESETS = [
        "Custom...",
        "dental office",
        "law firm",
        "accounting firm",
        "real estate agency",
        "medical clinic",
        "veterinary clinic",
        "insurance agency",
        "financial advisor",
        "construction company",
        "manufacturing company",
        "chiropractic office",
        "optometry clinic",
        "physical therapy clinic",
    ]

    category_choice = st.selectbox("Business Category", CATEGORY_PRESETS)
    if category_choice == "Custom...":
        category = st.text_input("Enter custom category", placeholder="e.g. architecture firm")
    else:
        category = category_choice

    location = st.text_input("Location", value="Austin, TX", placeholder="City, State")
    num_results = st.slider("Number of Leads", min_value=5, max_value=100, value=20, step=5)
    delay = st.slider("Delay between requests (sec)", min_value=0.5, max_value=5.0, value=1.5, step=0.5,
                      help="Higher = slower but less likely to get blocked")

    st.markdown("---")
    st.markdown("### 🎚️ Filters")
    min_score = st.slider("Minimum Lead Score", 0, 100, 0)
    require_email = st.checkbox("Only show leads with email")
    require_no_it = st.checkbox("Only show leads without IT staff")

    st.markdown("---")
    st.caption("Built for MSP owners · Powered by SerpAPI + Hunter.io")

# ── Main Area ──────────────────────────────────────────────────────────────────

st.markdown('<p class="main-title">🎯 MSP Lead Scraper</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Find SMB prospects that are prime candidates for managed IT services</p>', unsafe_allow_html=True)

# Initialize session state
if "leads_df" not in st.session_state:
    st.session_state.leads_df = None
if "scrape_running" not in st.session_state:
    st.session_state.scrape_running = False

# ── Search Button ──────────────────────────────────────────────────────────────

col_btn, col_info = st.columns([1, 3])
with col_btn:
    search_clicked = st.button("🚀 Find Leads", type="primary", use_container_width=True)
with col_info:
    if not serper_key and not serpapi_key:
        st.info("💡 No API key? The scraper will run with **mock data** so you can preview the UI. "
                "Get a free Serper key (2,500 searches/mo) at [serper.dev](https://serper.dev).")

# ── Vertical Recommender UI ───────────────────────────────────────────────────

with st.expander("💡 What's the best vertical to target in this location?", expanded=False):
    st.markdown(
        "Not sure which business type to go after? Click below and we'll scan **all verticals** "
        "in your location and rank them by MSP opportunity score."
    )
    rec_col1, rec_col2 = st.columns([1, 3])
    with rec_col1:
        analyze_clicked = st.button("🔍 Analyze Verticals", use_container_width=True)
    with rec_col2:
        top_n = st.slider("Show top N verticals", 3, 14, 5, key="top_n_slider")

    if analyze_clicked:
        if not location:
            st.warning("Enter a location in the sidebar first.")
        else:
            with st.spinner(f"Scanning {len(VERTICALS_META)} verticals in {location}..."):
                rec_df = analyze_verticals(location, top_n=top_n)

            st.success(f"✅ Analysis complete for **{location}**")

            # Medal display for top 3
            medals = ["🥇", "🥈", "🥉"]
            medal_cols = st.columns(min(3, len(rec_df)))
            for i, (col, (_, row)) in enumerate(zip(medal_cols, rec_df.iterrows())):
                with col:
                    st.markdown(f"""
                    <div style="background:#f0f4ff;border-radius:12px;padding:1rem;text-align:center;border:2px solid #4f46e5;">
                        <div style="font-size:2rem">{medals[i] if i < 3 else row['icon']}</div>
                        <div style="font-size:1.1rem;font-weight:700;margin:0.3rem 0">{row['icon']} {row['vertical']}</div>
                        <div style="font-size:1.8rem;font-weight:800;color:#4f46e5">{row['score']}<span style="font-size:1rem">/100</span></div>
                        <div style="font-size:0.8rem;color:#666;margin-top:0.3rem">{row['reason']}</div>
                        <div style="font-size:0.8rem;margin-top:0.5rem">
                            📍 {row['volume']} businesses found &nbsp;·&nbsp; ⭐ {row['avg_rating']} avg rating
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Full rankings table
            if len(rec_df) > 3:
                st.markdown("#### Full Rankings")
                display_rec = rec_df[["icon", "vertical", "score", "msp_fit", "volume", "avg_rating", "reason"]].copy()
                display_rec.columns = ["", "Vertical", "Opportunity Score", "MSP Fit", "# Found", "Avg Rating", "Why MSPs love this"]
                st.dataframe(display_rec, use_container_width=True, hide_index=False)

            # Quick-launch into scraper
            st.markdown("---")
            top_vertical = rec_df.iloc[0]["vertical"].lower()
            st.markdown(f"**🚀 Ready to scrape the top pick?**")
            if st.button(f"Search '{top_vertical}' in {location}", key="quick_launch"):
                st.session_state["quick_launch_category"] = top_vertical
                st.info(f"Category set to **{top_vertical}** — click **Find Leads** above to start!")

# Apply quick-launch category if set
if "quick_launch_category" in st.session_state:
    category = st.session_state["quick_launch_category"]

# ── Scraping Pipeline ──────────────────────────────────────────────────────────

if search_clicked and category and location:
    st.session_state.leads_df = None
    st.session_state.scrape_running = True

    st.markdown("---")
    status_text = st.empty()
    progress_bar = st.progress(0)
    results_placeholder = st.empty()

    leads = []

    with st.spinner(""):
        # Step 1: Search
        status_text.markdown(f"**🔍 Searching Google Maps for '{category}' in '{location}'...**")
        places = search_google_places(category, location, num_results)
        total = len(places)

        if total == 0:
            st.warning("No results found. Try a different category or location.")
        else:
            status_text.markdown(f"**✅ Found {total} businesses. Now scraping each one...**")

            for i, place in enumerate(places):
                lead = parse_place(place)

                # Scrape website
                website_data = scrape_website(lead["website"])
                lead.update(website_data)

                # Hunter.io enrichment
                domain = ""
                if lead["website"]:
                    try:
                        domain = urlparse(lead["website"]).netloc.replace("www.", "")
                    except Exception:
                        pass
                hunter_data = enrich_email_hunter(domain)
                lead.update(hunter_data)
                lead["domain"] = domain

                # Score
                lead["score"] = score_lead(lead)
                leads.append(lead)

                # Update progress
                pct = int((i + 1) / total * 100)
                progress_bar.progress(pct)
                status_text.markdown(
                    f"**Processing {i+1}/{total}:** {lead['business_name']} "
                    f"· Score: {lead['score']}/100 · {lead.get('scrape_status','')}"
                )
                time.sleep(delay)

    progress_bar.progress(100)
    status_text.markdown(f"**🎉 Done! Scraped {len(leads)} leads.**")

    # Build DataFrame
    col_order = [
        "score", "business_name", "category", "address", "phone",
        "website", "domain", "rating", "reviews",
        "emails_found", "hunter_email", "hunter_name", "hunter_confidence",
        "tech_stack", "has_it_mention", "scrape_status",
    ]
    df = pd.DataFrame(leads)

    # Deduplicate by domain (or business_name if no domain)
    if "domain" in df.columns:
        df = df.drop_duplicates(subset=["domain"], keep="first")
        mask_empty = df["domain"] == ""
        if mask_empty.any():
            deduped_empty = df[mask_empty].drop_duplicates(subset=["business_name"], keep="first")
            df = pd.concat([df[~mask_empty], deduped_empty], ignore_index=True)
    else:
        df = df.drop_duplicates(subset=["business_name"], keep="first")

    df = df[[c for c in col_order if c in df.columns]]
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    st.session_state.leads_df = df
    st.session_state.scrape_running = False

# ── Results Display ────────────────────────────────────────────────────────────

if st.session_state.leads_df is not None:
    df = st.session_state.leads_df.copy()

    # Apply filters
    if min_score > 0:
        df = df[df["score"] >= min_score]
    if require_email:
        has_scraped = df["emails_found"].str.len() > 0
        has_hunter = df["hunter_email"].str.len() > 0 if "hunter_email" in df.columns else False
        df = df[has_scraped | has_hunter]
    if require_no_it:
        df = df[df["has_it_mention"] == False]

    st.markdown("---")

    # ── KPI Metrics ──
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Leads", len(df))
    with c2:
        with_email = df["emails_found"].ne("").sum()
        st.metric("With Email", int(with_email))
    with c3:
        avg_score = df["score"].mean() if len(df) else 0
        st.metric("Avg Score", f"{avg_score:.0f}/100")
    with c4:
        hot = df[df["score"] >= 70]
        st.metric("Hot Leads (70+)", len(hot))
    with c5:
        no_it = df[df["has_it_mention"] == False]
        st.metric("No IT Staff", len(no_it))

    st.markdown("---")

    # ── Export Button ──
    csv_data = df.to_csv(index=False)
    col_exp1, col_exp2, _ = st.columns([1, 1, 4])
    with col_exp1:
        st.download_button(
            "📥 Download CSV",
            data=csv_data,
            file_name=f"leads_{category.replace(' ','_')}_{location.replace(', ','_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_exp2:
        st.download_button(
            "📋 Copy as JSON",
            data=df.to_json(orient="records", indent=2),
            file_name="leads.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("### 📋 Lead Results")

    # ── Score color helper ──
    def color_score(val):
        if val >= 70:
            return "background-color: #dcfce7; color: #16a34a; font-weight: bold"
        elif val >= 40:
            return "background-color: #fef9c3; color: #d97706; font-weight: bold"
        else:
            return "background-color: #fee2e2; color: #dc2626; font-weight: bold"

    def color_it(val):
        if val:
            return "background-color: #fee2e2"
        return "background-color: #dcfce7"

    # Display columns
    display_cols = ["score", "business_name", "phone", "emails_found",
                    "hunter_email", "hunter_name", "tech_stack", "has_it_mention",
                    "rating", "reviews", "address"]
    display_df = df[[c for c in display_cols if c in df.columns]]

    styled = (
        display_df.style
        .map(color_score, subset=["score"])
        .map(color_it, subset=["has_it_mention"])
    )

    st.dataframe(styled, use_container_width=True, height=500)

    # ── Lead Detail Expander ──
    st.markdown("---")
    st.markdown("### 🔎 Lead Detail View")
    lead_names = df["business_name"].tolist()
    selected_name = st.selectbox("Select a lead to inspect", lead_names)

    if selected_name:
        row = df[df["business_name"] == selected_name].iloc[0]

        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.markdown(f"#### {row['business_name']}")
            score = row['score']
            if score >= 70:
                st.success(f"⭐ Lead Score: {score}/100 — Hot Lead")
            elif score >= 40:
                st.warning(f"🔸 Lead Score: {score}/100 — Warm Lead")
            else:
                st.error(f"🔻 Lead Score: {score}/100 — Cold Lead")

            st.markdown(f"📍 **Address:** {row.get('address','—')}")
            st.markdown(f"📞 **Phone:** {row.get('phone','—')}")
            st.markdown(f"🌐 **Website:** {row.get('website','—')}")
            st.markdown(f"⭐ **Rating:** {row.get('rating','—')} ({row.get('reviews','—')} reviews)")

        with dcol2:
            st.markdown("#### 📧 Contact Info")
            st.markdown(f"**Scraped Emails:** {row.get('emails_found','—') or '—'}")
            st.markdown(f"**Hunter Email:** {row.get('hunter_email','—') or '—'}")
            st.markdown(f"**Contact Name:** {row.get('hunter_name','—') or '—'}")
            st.markdown(f"**Hunter Confidence:** {row.get('hunter_confidence','—') or '—'}%")

            st.markdown("#### 💻 Tech Stack")
            tech = row.get("tech_stack", "")
            if tech:
                for t in tech.split(", "):
                    st.markdown(f"- {t}")
            else:
                st.markdown("_No tech signals detected_")

            has_it = row.get("has_it_mention", False)
            if has_it:
                st.warning("⚠️ This business mentions IT staff — may already have internal IT")
            else:
                st.success("✅ No IT staff mentioned — great MSP prospect!")

# ── Empty State ────────────────────────────────────────────────────────────────

elif not search_clicked:
    st.markdown("---")
    st.markdown("""
    ### 👋 How to use this tool

    1. **Enter your API keys** in the sidebar (or skip for mock data)
    2. **Choose a business category** — dental offices, law firms, accounting firms work great
    3. **Set your location** — city and state
    4. **Click Find Leads** and watch it run in real time
    5. **Filter, review, and export** your leads as CSV or JSON

    ---

    #### 🏆 Best target categories for MSPs

    | Category | Why they're great prospects |
    |----------|----------------------------|
    | Dental offices | High revenue, no IT staff, compliance needs (HIPAA) |
    | Law firms | Sensitive data, strict uptime needs, usually no IT |
    | Accounting firms | Compliance needs, seasonal crunch, trust-driven |
    | Medical clinics | HIPAA compliance, EMR systems, always need IT |
    | Real estate agencies | Cloud-heavy, distributed teams, tight budgets |
    """)
