import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# --- CSS: Soft Pink Background + Clean UI ---
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap');

body {
    background-color: #f8d7da;  /* soft pink */
    font-family: 'Quicksand', sans-serif;
    color: #3e2723;
    margin: 0;
    padding: 0;
}

.main-container {
    background: white;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    margin-bottom: 30px;
}

h1, h2, h3 {
    color: #ad1457;
    font-weight: 700;
    margin-bottom: 15px;
}

h4 {
    color: #880e4f;
    margin-bottom: 10px;
}

.stButton > button {
    background-color: #f48fb1;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 8px 20px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.stButton > button:hover {
    background-color: #ec407a;
}

.element-container {
    padding: 12px 0;
    margin-bottom: 25px;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 40px 0;
}

/* Hide empty Streamlit components that sometimes show empty bubbles */
[data-testid="stExpander"] > div > div:empty,
[data-testid="stVerticalBlock"] > div > div:empty,
div.css-1v0mbdj.etr89bj2 {
    display: none !important;
}
</style>
"""

st.set_page_config(page_title="🌸 Cottage Campaign Dashboard", layout="wide")
st.markdown(page_bg, unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("## 🐝 Campaign Analysis Dashboard 🌸")
st.markdown("*Visualize campaign performance and extract actionable insights.*")

uploaded_file = st.file_uploader("📁 Upload your CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    required = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    missing_cols = [col for col in required if col not in df.columns]
    if missing_cols:
        st.error(f"🚫 Missing required columns: {missing_cols}")
        st.stop()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)
    df.dropna(subset=['date'], inplace=True)

    if df.empty:
        st.warning("⚠️ The uploaded data is empty after cleaning.")
        st.stop()

    st.markdown("### 🎯 Filter Your Data")
    platforms = ['All'] + sorted(df['platform'].dropna().unique())
    sentiments = ['All'] + sorted(df['sentiment'].dropna().unique())
    locations = ['All'] + sorted(df['location'].dropna().unique())
    media_types = ['All'] + sorted(df['media_type'].dropna().unique())

    col1, col2, col3, col4 = st.columns(4)
    f_platform = col1.selectbox("Platform", platforms)
    f_sentiment = col2.selectbox("Sentiment", sentiments)
    f_location = col3.selectbox("Location", locations)
    f_media = col4.selectbox("Media Type", media_types)

    col5, col6 = st.columns(2)
    start_date = col5.date_input("Start Date", df['date'].min().date())
    end_date = col6.date_input("End Date", df['date'].max().date())

    filtered = df.copy()
    if f_platform != 'All':
        filtered = filtered[filtered['platform'] == f_platform]
    if f_sentiment != 'All':
        filtered = filtered[filtered['sentiment'] == f_sentiment]
    if f_location != 'All':
        filtered = filtered[filtered['location'] == f_location]
    if f_media != 'All':
        filtered = filtered[filtered['media_type'] == f_media]
    filtered = filtered[(filtered['date'].dt.date >= start_date) & (filtered['date'].dt.date <= end_date)]

    if filtered.empty:
        st.warning("⚠️ No data matches your filters. Please adjust filters.")
    else:

        def get_top_sentiments(df):
            top3 = df['sentiment'].value_counts().head(3)
            return [f"🔎 {s}: {c} mentions" for s, c in top3.items()]

        def get_trends(df):
            trend = df.groupby('date')['engagements'].sum()
            if len(trend) < 2:
                return [f"📈 Only {len(trend)} day(s) data available for trend."]
            top3_dates = trend.sort_values(ascending=False).head(3)
            out = [f"📈 Highest engagement on {d.strftime('%Y-%m-%d')}: {v}" for d, v in top3_dates.items()]
            change = trend.pct_change().fillna(0).iloc[-1]
            arrow = '⬆️' if change > 0 else ('⬇️' if change < 0 else '➡️')
            out.append(f"📊 Recent engagement trend: {arrow} {abs(change)*100:.2f}% change from previous day")
            return out

        def get_platforms(df):
            top3 = df.groupby('platform')['engagements'].sum().sort_values(ascending=False).head(3)
            return [f"📱 {p}: {v} total engagements" for p, v in top3.items()]

        def get_media_mix(df):
            top3 = df['media_type'].value_counts().head(3)
            return [f"🎞️ {m}: {v} posts" for m, v in top3.items()]

        def get_locations(df):
            top3 = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(3)
            return [f"📍 {l}: {v} engagements" for l, v in top3.items()]

        st.markdown("## 📊 Visualizations and Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🧁 Sentiment Breakdown")
            fig1 = px.pie(filtered, names='sentiment', color_discrete_sequence=px.colors.sequential.Pinkyl)
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("**Top 3 Sentiments:**")
            for s in get_top_sentiments(filtered):
                st.markdown(f"- {s}")

        with col2:
            st.markdown("### 🌱 Engagement Trend")
            trend = filtered.groupby('date')['engagements'].sum().reset_index()
            fig2 = px.line(trend, x='date', y='engagements', line_shape='spline', markers=True,
                           color_discrete_sequence=['#ad1457'])
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("**Top 3 Engagement Trend Insights:**")
            for t in get_trends(filtered):
                st.markdown(f"- {t}")

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### 🗂️ Platforms by Engagement")
            platform_data = filtered.groupby('platform')['engagements'].sum().reset_index()
            fig3 = px.bar(platform_data, x='platform', y='engagements', color='platform',
                          color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("**Top 3 Platforms:**")
            for p in get_platforms(filtered):
                st.markdown(f"- {p}")

        with col4:
            st.markdown("### 🎞️ Media Types Breakdown")
            fig4 = px.pie(filtered, names='media_type', color_discrete_sequence=px.colors.sequential.RdPu)
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown("**Top 3 Media Types:**")
            for m in get_media_mix(filtered):
                st.markdown(f"- {m}")

        st.markdown("### 📍 Top Locations by Engagement")
        loc = filtered.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).reset_index()
        fig5 = px.bar(loc, x='location', y='engagements', color='location',
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("**Top 3 Locations:**")
        for l in get_locations(filtered):
            st.markdown(f"- {l}")

        # PDF Export
        class PDFReport(FPDF):
            def header(self):
                self.set_font('Helvetica', 'B', 14)
                self.cell(0, 10, 'Campaign Insights Report 🌸', 0, 1, 'C')
            def chapter_title(self, title):
                self.set_font('Helvetica', 'B', 12)
                self.cell(0, 10, title, 0, 1)
            def chapter_body(self, body):
                self.set_font('Helvetica', '', 11)
                self.multi_cell(0, 10, body)
                self.ln()

        def create_pdf():
            pdf = PDFReport()
            pdf.add_page()
            pdf.chapter_title("Sentiment Insights")
            pdf.chapter_body("\n".join(get_top_sentiments(filtered)))
            pdf.chapter_title("Engagement Trends")
            pdf.chapter_body("\n".join(get_trends(filtered)))
            pdf.chapter_title("Top Platforms")
            pdf.chapter_body("\n".join(get_platforms(filtered)))
            pdf.chapter_title("Media Type Summary")
            pdf.chapter_body("\n".join(get_media_mix(filtered)))
            pdf.chapter_title("Top Locations")
            pdf.chapter_body("\n".join(get_locations(filtered)))
            return pdf.output(dest='S').encode('latin1')

        st.markdown("### 📤 Export Report")
        if st.button("📄 Export to PDF"):
            b64 = base64.b64encode(create_pdf()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="campaign_report.pdf">📥 Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center; color:#880e4f;'>🌸 Powered by Your Friendly Bot 💗</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
