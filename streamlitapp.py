import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# --- CSS: Cottage Flowery Theme with readability ---
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap');

body {
    background-image: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1600&q=80');
    background-size: cover;
    background-attachment: fixed;
    font-family: 'Quicksand', sans-serif;
    color: #2f2f2f;
}

.main-container {
    background: rgba(255, 255, 255, 0.92);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

h1, h2, h3 {
    color: #4caf50;
    font-weight: 700;
}

h4 {
    color: #e91e63;
}

.stButton > button {
    background-color: #ffcccb;
    color: #2e7d32;
    border: none;
    border-radius: 12px;
    padding: 8px 20px;
    font-size: 16px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #ffe0b2;
    color: #1b5e20;
}

.element-container {
    background: white;
    border-radius: 16px;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    padding: 12px;
    margin-bottom: 25px;
}
</style>
"""

st.set_page_config(page_title="🌷 Cottage Campaign Dashboard", layout="wide")
st.markdown(page_bg, unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("## 🐝 Campaign Analysis Dashboard 🌼")
st.markdown("*Visualize campaign performance and extract actionable insights.* 🍃")

# --- File upload
uploaded_file = st.file_uploader("📁 Upload your CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    required = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    if not all(col in df.columns for col in required):
        st.error(f"Missing required columns: {list(df.columns)}")
        st.stop()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)
    df.dropna(subset=['date'], inplace=True)

    # --- Filters
    st.markdown("### 🎯 Filter Your Data ✏️")
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

    # --- Helper insights
    def get_top_sentiments(df):
        return [f"🔎 {s}: {c}" for s, c in df['sentiment'].value_counts().head(3).items()]
    
    def get_trends(df):
        trend = df.groupby('date')['engagements'].sum()
        increase = trend.pct_change().fillna(0)
        top = trend.sort_values(ascending=False).head(3)
        out = [f"📈 Highest on {d.strftime('%Y-%m-%d')}: {v}" for d, v in top.items()]
        out.append(f"📊 Recent trend: {'⬆️' if increase.iloc[-1]>0 else '⬇️'} {abs(increase.iloc[-1]*100):.2f}%")
        return out
    
    def get_platforms(df):
        return [f"📱 {p}: {v} engagements" for p, v in df.groupby('platform')['engagements'].sum().sort_values(ascending=False).head(3).items()]
    
    def get_media_mix(df):
        return [f"🎞️ {m}: {v} entries" for m, v in df['media_type'].value_counts().head(3).items()]
    
    def get_locations(df):
        return [f"📍 {l}: {v} engagements" for l, v in df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(3).items()]

    # --- Display charts
    st.markdown("## 📊 Visualizations")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🧁 Sentiment Breakdown")
        fig1 = px.pie(filtered, names='sentiment', title='', color_discrete_sequence=px.colors.sequential.Pinkyl)
        st.plotly_chart(fig1, use_container_width=True)
        for s in get_top_sentiments(filtered):
            st.markdown(f"- {s}")
    
    with col2:
        st.markdown("#### 🌱 Engagement Trend")
        trend = filtered.groupby('date')['engagements'].sum().reset_index()
        fig2 = px.line(trend, x='date', y='engagements', line_shape='spline', markers=True)
        st.plotly_chart(fig2, use_container_width=True)
        for t in get_trends(filtered):
            st.markdown(f"- {t}")

    st.markdown("### 🗂️ Platforms & Media")
    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(filtered.groupby('platform')['engagements'].sum().reset_index(), x='platform', y='engagements', color='platform')
        st.plotly_chart(fig3, use_container_width=True)
        for p in get_platforms(filtered):
            st.markdown(f"- {p}")
    with col4:
        fig4 = px.pie(filtered, names='media_type', title='', color_discrete_sequence=px.colors.sequential.RdPu)
        st.plotly_chart(fig4, use_container_width=True)
        for m in get_media_mix(filtered):
            st.markdown(f"- {m}")

    st.markdown("### 📍 Top Locations")
    loc = filtered.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).reset_index()
    fig5 = px.bar(loc, x='location', y='engagements', color='location')
    st.plotly_chart(fig5, use_container_width=True)
    for l in get_locations(filtered):
        st.markdown(f"- {l}")

    # --- PDF Generator
    class PDFReport(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, 'Campaign Insights Report 🌼', 0, 1, 'C')
        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title, 0, 1)
        def chapter_body(self, body):
            self.set_font('Arial', '', 11)
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

    st.markdown("### 📤 Export")
    if st.button("📄 Export to PDF"):
        b64 = base64.b64encode(create_pdf()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="campaign_report.pdf">📥 Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center'>🌷 Hope this helped! Made with 💗 by Zulfa 🐣</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


