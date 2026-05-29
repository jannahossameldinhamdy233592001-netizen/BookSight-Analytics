import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

from groq import Groq

# ══════════════════════════════════════════════
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
# ══════════════════════════════════════════════

st.set_page_config(
    page_title="📚 BookSight Analytics",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg:        #0A0812;
    --surface:   #100D1C;
    --card:      #160F2A;
    --card2:     #1C1535;
    --border:    #2A1F4E;
    --border2:   #3D2D6E;
    --p1:        #A78BFA;
    --p2:        #7C3AED;
    --p3:        #C4B5FD;
    --p4:        #6D28D9;
    --pink:      #F472B6;
    --cyan:      #67E8F9;
    --green:     #86EFAC;
    --text:      #EDE9FE;
    --muted:     #6B5F8A;
    --muted2:    #9480C4;
}

* { font-family: 'Plus Jakarta Sans', sans-serif; box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: var(--bg) !important;
    color: var(--text) !important;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ── KPI cards ── */
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 28px; }
.kpi-card {
    background: linear-gradient(145deg, var(--card), var(--card2));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px 16px 18px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform .25s, border-color .25s;
}
.kpi-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(167,139,250,.08), rgba(124,58,237,.04));
    pointer-events: none;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 16px; right: 16px;
    height: 2px;
    border-radius: 0 0 4px 4px;
    background: linear-gradient(90deg, var(--p2), var(--p1), var(--pink));
}
.kpi-card:hover { transform: translateY(-3px); border-color: var(--border2); }
.kpi-icon { font-size: 1.5rem; margin-bottom: 10px; display: block; }
.kpi-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--p3);
    line-height: 1;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--muted2);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Section header ── */
.sec-hdr {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--p3);
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 14px;
}

/* ── Page title ── */
.page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--p3) 0%, var(--pink) 60%, var(--cyan) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2px;
    line-height: 1.1;
}
.page-sub { color: var(--muted2); font-size: 0.85rem; margin-bottom: 26px; }

/* ── Chat ── */
.chat-wrap { max-height: 480px; overflow-y: auto; padding: 4px 0 12px; }
.chat-user {
    background: linear-gradient(135deg, var(--p2), #4C1D95);
    border-radius: 16px 16px 4px 16px;
    padding: 11px 16px;
    margin: 6px 0 6px 18%;
    color: #EDE9FE;
    font-size: 0.88rem;
    line-height: 1.6;
    box-shadow: 0 4px 16px rgba(124,58,237,.3);
}
.chat-bot {
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: 16px 16px 16px 4px;
    padding: 13px 16px;
    margin: 6px 18% 6px 0;
    color: var(--text);
    font-size: 0.88rem;
    line-height: 1.85;
    white-space: pre-wrap;
}
.chat-lbl { font-size: 0.72rem; color: var(--p1); font-weight: 700; margin-bottom: 5px; letter-spacing:.05em; }

/* ── Sidebar ── */
[data-testid="stRadio"] label { font-size: 0.88rem !important; padding: 5px 0 !important; }
[data-testid="stSelectbox"] > div, [data-testid="stMultiSelect"] > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 14px !important;
}
[data-testid="stTextInput"] input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}
/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--p2), var(--p4)) !important;
    border: none !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
.stButton > button:hover { opacity: .85 !important; }

#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("all_books_with_categories.csv", encoding="latin-1")
    df["Rating_Num"] = df["Rating"].map({"One":1,"Two":2,"Three":3,"Four":4,"Five":5})
    df["Price_Num"] = df["Price"].str.replace("£","",regex=False).astype(float)
    df["Value_Score"] = (df["Rating_Num"] / df["Price_Num"] * 10).round(2)
    df["Price_Segment"] = pd.cut(df["Price_Num"], bins=[0,20,40,60],
        labels=["Budget (< £20)","Mid-range (£20–40)","Premium (> £40)"])
    return df

df = load_data()

THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#EDE9FE"),
    margin=dict(t=40, b=30, l=20, r=20),
)
COLORS = ["#A78BFA","#F472B6","#67E8F9","#86EFAC","#FCD34D","#C084FC","#38BDF8","#FB923C"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:24px 0 28px'>
        <div style='font-size:2.6rem;filter:drop-shadow(0 0 12px #7C3AED)'>📚</div>
        <div style='font-family:Space Grotesk,sans-serif;font-size:1.3rem;font-weight:700;
                    background:linear-gradient(135deg,#C4B5FD,#F472B6);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:6px'>
            BookSight
        </div>
        <div style='font-size:0.72rem;color:#6B5F8A;margin-top:3px;letter-spacing:.06em'>ANALYTICS DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", ["🏠  Overview","📊  Analytics","🤖  AI Assistant","🔍  Explorer"],
                    label_visibility="collapsed")

    st.markdown("<hr style='border-color:#2A1F4E;margin:12px 0'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.72rem;color:#6B5F8A;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px'>⚙ Filters</div>", unsafe_allow_html=True)

    all_cats = sorted(df["Category"].unique())
    selected_cats = st.multiselect("Categories", all_cats, default=all_cats, placeholder="All")
    price_range = st.slider("Price (£)", 0.0, 60.0, (0.0, 60.0), 1.0)
    min_rating = st.slider("Min Rating ⭐", 1, 5, 1)

    st.markdown("<hr style='border-color:#2A1F4E;margin:12px 0'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.72rem;color:#6B5F8A'>📦 {len(df):,} books · {df['Category'].nunique()} cats</div>", unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
fdf = df.copy()
if selected_cats:
    fdf = fdf[fdf["Category"].isin(selected_cats)]
fdf = fdf[(fdf["Price_Num"]>=price_range[0]) & (fdf["Price_Num"]<=price_range[1])]
fdf = fdf[fdf["Rating_Num"]>=min_rating]

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "🏠  Overview":
    st.markdown('<div class="page-title">Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">High-level summary of your books dataset</div>', unsafe_allow_html=True)

    top_cat   = fdf["Category"].value_counts().idxmax() if len(fdf) else "N/A"
    best_val  = fdf.groupby("Category")["Value_Score"].mean().idxmax() if len(fdf) else "N/A"

    def kpi(icon, val, label):
        return f"""<div class="kpi-card">
            <span class="kpi-icon">{icon}</span>
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>"""

    kpis_html = "".join([
        kpi("📚", f"{len(fdf):,}",                             "Total Books"),
        kpi("⭐", f"{fdf['Rating_Num'].mean():.2f}",           "Avg Rating"),
        kpi("💷", f"£{fdf['Price_Num'].mean():.2f}",           "Avg Price"),
        kpi("🔺", f"£{fdf['Price_Num'].max():.2f}",            "Max Price"),
        kpi("🔻", f"£{fdf['Price_Num'].min():.2f}",            "Min Price"),
        kpi("🏆", (top_cat[:13]+"…" if len(top_cat)>13 else top_cat), "Top Category"),
        kpi("💎", (best_val[:13]+"…" if len(best_val)>13 else best_val), "Best Value"),
        kpi("🗂",  str(fdf["Category"].nunique()),              "Categories"),
    ])
    st.markdown(f'<div class="kpi-grid">{kpis_html}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2,1])
    with c1:
        st.markdown('<div class="sec-hdr">📊 Books per Category — Top 15</div>', unsafe_allow_html=True)
        t = fdf["Category"].value_counts().head(15).reset_index()
        t.columns = ["Category","Count"]
        fig = px.bar(t, x="Count", y="Category", orientation="h", color="Count",
                     color_continuous_scale=["#2A1F4E","#7C3AED","#C4B5FD"])
        fig.update_layout(**THEME, height=390, showlegend=False, coloraxis_showscale=False,
                          yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-hdr">🍩 Category Share</div>', unsafe_allow_html=True)
        t8 = fdf["Category"].value_counts().head(8).reset_index()
        t8.columns = ["Category","Count"]
        fig = px.pie(t8, names="Category", values="Count", hole=.55,
                     color_discrete_sequence=COLORS)
        fig.update_layout(**THEME, height=390, legend=dict(font=dict(size=10)))
        fig.update_traces(textposition='inside', textinfo='percent')
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-hdr">⭐ Rating Distribution</div>', unsafe_allow_html=True)
        r = fdf["Rating"].value_counts().reindex(["One","Two","Three","Four","Five"]).reset_index()
        r.columns = ["Rating","Count"]
        fig = px.bar(r, x="Rating", y="Count", color="Count",
                     color_continuous_scale=["#4C1D95","#7C3AED","#C4B5FD"])
        fig.update_layout(**THEME, height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-hdr">🏷 Price Segments</div>', unsafe_allow_html=True)
        seg = fdf["Price_Segment"].value_counts().reset_index()
        seg.columns = ["Segment","Count"]
        fig = px.pie(seg, names="Segment", values="Count", hole=.5,
                     color_discrete_map={
                         "Budget (< £20)":"#86EFAC",
                         "Mid-range (£20–40)":"#A78BFA",
                         "Premium (> £40)":"#F472B6"})
        fig.update_layout(**THEME, height=300)
        st.plotly_chart(fig, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ANALYTICS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📊  Analytics":
    st.markdown('<div class="page-title">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Deep dive into pricing, ratings & value insights</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-hdr">🔵 Price vs Rating</div>', unsafe_allow_html=True)
        fig = px.scatter(fdf, x="Price_Num", y="Rating_Num", color="Category",
                         hover_data=["Title"], color_discrete_sequence=COLORS,
                         labels={"Price_Num":"Price (£)","Rating_Num":"Rating"})
        fig.update_layout(**THEME, height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-hdr">💷 Price Distribution</div>', unsafe_allow_html=True)
        fig = px.histogram(fdf, x="Price_Num", nbins=30, color_discrete_sequence=["#7C3AED"])
        fig.update_layout(**THEME, height=350, xaxis_title="Price (£)")
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-hdr">📦 Price Spread by Category — Top 10</div>', unsafe_allow_html=True)
        top10 = fdf["Category"].value_counts().head(10).index
        fig = px.box(fdf[fdf["Category"].isin(top10)], x="Category", y="Price_Num",
                     color="Category", color_discrete_sequence=COLORS,
                     labels={"Price_Num":"Price (£)"})
        fig.update_layout(**THEME, height=350, showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-hdr">⭐ Avg Rating by Category — Top 15</div>', unsafe_allow_html=True)
        ar = fdf.groupby("Category")["Rating_Num"].mean().reset_index().sort_values("Rating_Num",ascending=False).head(15)
        fig = px.bar(ar, x="Category", y="Rating_Num", color="Rating_Num",
                     color_continuous_scale=["#4C1D95","#A78BFA","#F472B6"],
                     range_color=[1,5], labels={"Rating_Num":"Avg Rating"})
        fig.update_layout(**THEME, height=350, coloraxis_showscale=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-hdr">💎 Value for Money — Top 15</div>', unsafe_allow_html=True)
        vm = fdf.groupby("Category")["Value_Score"].mean().reset_index().sort_values("Value_Score",ascending=False).head(15)
        fig = px.bar(vm, x="Category", y="Value_Score", color="Value_Score",
                     color_continuous_scale=["#2A1F4E","#7C3AED","#C4B5FD"],
                     labels={"Value_Score":"Value Score"})
        fig.update_layout(**THEME, height=350, coloraxis_showscale=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-hdr">🫧 Bubble: Avg Price vs Avg Rating</div>', unsafe_allow_html=True)
        agg = fdf.groupby("Category").agg(
            Avg_Price=("Price_Num","mean"),
            Avg_Rating=("Rating_Num","mean"),
            Count=("Title","count")).reset_index()
        fig = px.scatter(agg, x="Avg_Price", y="Avg_Rating", size="Count",
                         color="Category", hover_name="Category",
                         color_discrete_sequence=COLORS,
                         labels={"Avg_Price":"Avg Price (£)","Avg_Rating":"Avg Rating"})
        fig.update_layout(**THEME, height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec-hdr">🔥 Heatmap: Category × Rating</div>', unsafe_allow_html=True)
    top12 = fdf["Category"].value_counts().head(12).index
    pivot = fdf[fdf["Category"].isin(top12)].pivot_table(
        index="Category", columns="Rating", values="Title", aggfunc="count", fill_value=0)
    order = [c for c in ["One","Two","Three","Four","Five"] if c in pivot.columns]
    fig = go.Figure(go.Heatmap(
        z=pivot[order].values, x=order, y=pivot.index.tolist(),
        colorscale=[[0,"#100D1C"],[0.5,"#7C3AED"],[1,"#F472B6"]],
        hovertemplate="Category: %{y}<br>Rating: %{x}<br>Count: %{z}<extra></extra>"
    ))
    fig.update_layout(**THEME, height=420)
    st.plotly_chart(fig, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AI ASSISTANT
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🤖  AI Assistant":
    st.markdown('<div class="page-title">AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ask anything about your books dataset — powered by Groq & LLaMA</div>', unsafe_allow_html=True)

    @st.cache_data
    def build_summary():
        stats = []
        for cat in df["Category"].unique():
            sub = df[df["Category"]==cat]
            stats.append({"Category":cat,"Count":len(sub),
                "Avg_Price":round(sub["Price_Num"].mean(),2),
                "Avg_Rating":round(sub["Rating_Num"].mean(),2),
                "Min_Price":round(sub["Price_Num"].min(),2),
                "Max_Price":round(sub["Price_Num"].max(),2)})
        return (f"إجمالي الكتب: {len(df)}\nعدد الكاتيجوريز: {df['Category'].nunique()}\n"
                f"أغلى كتاب: {df.loc[df['Price_Num'].idxmax(),'Title']} بسعر £{df['Price_Num'].max():.2f}\n"
                f"أرخص كتاب: {df.loc[df['Price_Num'].idxmin(),'Title']} بسعر £{df['Price_Num'].min():.2f}\n"
                f"متوسط السعر: £{df['Price_Num'].mean():.2f}\nمتوسط الريتينج: {df['Rating_Num'].mean():.2f}\n"
                f"توزيع الريتينج: {df['Rating'].value_counts().to_dict()}\n"
                f"إحصائيات الكاتيجوريز:\n{json.dumps(stats, ensure_ascii=False)}")

    SYS = ("أنت مساعد ذكي متخصص في تحليل داتاسيت كتب. إليك الداتا:\n" + build_summary() +
           "\nقواعد: أجب بدقة واختصار، استخدم الأرقام الحقيقية، استخدم إيموجي، أجب بلغة السؤال. "
           "لا تكرر نفسك ولا تطول بدون داعي.")

    def ask_groq(q, hist):
        try:
            client = Groq(api_key=GROQ_API_KEY)
            msgs = [{"role":"system","content":SYS}]
            for h in hist[-4:]:
                msgs += [{"role":"user","content":h["user"]},{"role":"assistant","content":h["bot"]}]
            msgs.append({"role":"user","content":q})
            r = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, max_tokens=512)
            return r.choices[0].message.content
        except Exception as e:
            return f"❌ خطأ: {str(e)}"

    # Init session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "submitted_q" not in st.session_state:
        st.session_state.submitted_q = ""

    # Suggestion chips
    SUGG = ["أغلى كتاب؟","أرخص كاتيجوري؟","أحسن value for money؟","قارن Fiction و Mystery","كام كتاب 5 نجوم؟"]
    cols = st.columns(len(SUGG))
    for i, s in enumerate(SUGG):
        if cols[i].button(s, use_container_width=True, key=f"sugg_{i}"):
            st.session_state.submitted = True
            st.session_state.submitted_q = s

    st.markdown("<br>", unsafe_allow_html=True)

    # Display chat
    chat_html = ""
    if not st.session_state.chat_history:
        chat_html = '<div class="chat-bot"><div class="chat-lbl">🤖 BOOKSIGHT AI</div>أهلاً! اسألني أي سؤال عن الكتب 📚<br>مثلاً: أغلى كتاب؟ أرخص كاتيجوري؟ قارن بين كاتيجوريتين؟</div>'
    else:
        for h in st.session_state.chat_history:
            chat_html += f'<div class="chat-user">{h["user"]}</div>'
            chat_html += f'<div class="chat-bot"><div class="chat-lbl">🤖 BOOKSIGHT AI</div>{h["bot"]}</div>'
    st.markdown(f'<div class="chat-wrap">{chat_html}</div>', unsafe_allow_html=True)

    # Input row
    c1, c2, c3 = st.columns([5,1,1])
    with c1:
        user_q = st.text_input("", placeholder="اسأل أي سؤال عن الكتب...",
                               label_visibility="collapsed", key="chat_input")
    with c2:
        if st.button("إرسال ➤", use_container_width=True, key="send_btn"):
            if user_q.strip():
                st.session_state.submitted = True
                st.session_state.submitted_q = user_q.strip()
    with c3:
        if st.button("🗑 مسح", use_container_width=True, key="clear_btn"):
            st.session_state.chat_history = []
            st.session_state.submitted = False
            st.session_state.submitted_q = ""
            st.rerun()

    # Process submission ONCE
    if st.session_state.submitted and st.session_state.submitted_q:
        q = st.session_state.submitted_q
        st.session_state.submitted = False
        st.session_state.submitted_q = ""
        with st.spinner("🤔 بفكر..."):
            ans = ask_groq(q, st.session_state.chat_history)
        st.session_state.chat_history.append({"user": q, "bot": ans})
        st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — EXPLORER
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🔍  Explorer":
    st.markdown('<div class="page-title">Data Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Browse and search through all books</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        search = st.text_input("🔍 Search title", placeholder="e.g. Sapiens...")
    with c2:
        sort_by = st.selectbox("Sort by", ["Price (High→Low)","Price (Low→High)","Rating (High→Low)","Rating (Low→High)"])
    with c3:
        show_n = st.selectbox("Show", [25,50,100,250,500,1000], index=1)

    result = fdf.copy()
    if search:
        result = result[result["Title"].str.lower().str.contains(search.lower(), na=False)]
    scol, sasc = {"Price (High→Low)":("Price_Num",False),"Price (Low→High)":("Price_Num",True),
                  "Rating (High→Low)":("Rating_Num",False),"Rating (Low→High)":("Rating_Num",True)}[sort_by]
    result = result.sort_values(scol, ascending=sasc).head(show_n)

    st.markdown(f"<div style='color:#6B5F8A;font-size:.82rem;margin-bottom:10px'>Showing {len(result):,} books</div>", unsafe_allow_html=True)
    display = result[["Title","Category","Rating","Price_Num"]].rename(columns={"Price_Num":"Price (£)"})
    st.dataframe(display, use_container_width=True, height=500,
                 column_config={
                     "Title": st.column_config.TextColumn("📖 Title", width="large"),
                     "Category": st.column_config.TextColumn("🗂 Category"),
                     "Rating": st.column_config.TextColumn("⭐ Rating"),
                     "Price (£)": st.column_config.NumberColumn("💷 Price", format="£%.2f"),
                 })

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Shown", f"{len(result):,}")
    c2.metric("Avg Price", f"£{result['Price_Num'].mean():.2f}")
    c3.metric("Avg Rating", f"{result['Rating_Num'].mean():.2f} ⭐")
    c4.metric("Categories", result["Category"].nunique())