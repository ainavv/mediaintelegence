import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# --- PDF generation helper ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(34, 85, 34)
        self.cell(0, 10, 'Interactive Media Intelligence Dashboard Report', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(255, 241, 196)
        self.set_text_color(204, 0, 102)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(51, 51, 51)
        self.multi_cell(0, 10, body)
        self.ln()

# --- Insight functions ---
def get_top_sentiments(df):
    counts = df['sentiment'].value_counts().head(3)
    return [f"{sentiment}: {count}" for sentiment, count in counts.items()]

def get_engagement_trend_insights(df):
    trend = df.groupby('date')['engagements'].sum()
    increase = trend.pct_change().fillna(0)
    top_dates = trend.sort_values(ascending=False).head(3)
    insights = [f"Highest engagement on {date.strftime('%Y-%m-%d')}: {val}" for date, val in top_dates.items()]
    change = increase.iloc[-1]
    if change > 0:
        insights.append(f"Engagements increased by {change*100:.2f}% recently")
    else:
        insights.append(f"Engagements decreased by {abs(change*100):.2f}% recently")
    return insights[:3]

def get_platform_engagements_insights(df):
    platform_sum = df.groupby('platform')['engagements'].sum().sort_values(ascending=False).head(3)
    return [f"{platform}: {val} engagements" for platform, val in platform_sum.items()]

def get_media_type_mix_insights(df):
    media_counts = df['media_type'].value_counts().head(3)
    return [f"{media}: {count} entries" for media, count in media_counts.items()]

def get_top_locations_insights(df):
    location_sum = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(3)
    return [f"{location}: {val} engagements" for location, val in location_sum.items()]

# --- Streamlit Config ---
st.set_page_config(page_title="🌷 Campaign Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- CSS Styling ---
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap');
body {
    background-image: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1470&q=80');
    background-size: cover;
    background-attachment: fixed;
    font-family: 'Quicksand', sans-serif;
    color: #37474f;
}
.main {
    background: rgba(255, 255, 255, 0.93);
    border-radius: 20px;
    padding: 30px 40px;
    box-shadow: 0 12px 24px rgba(0,0,0,0.15);
}
h1, h2, h3 {
    background: linear-gradient(to right, #ffb6b9, #fae3d9, #b5ead7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
}
h4 { color: #e91e63; font-weight: 600; }
.stButton > button {
    background-color: #ffcdd2;
    color: #4e342e;
    border-radius: 12px;
    padding: 10px 22px;
    font-weight: bold;
    font-size: 16px;
    border: none;
    box-shadow: 0 4px 8px rgba(255,182,193, 0.4);
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background-color: #ffe0b2;
    color: #2e7d32;
}
.stMarkdown p {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #455a64;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)
st.markdown('<div class="main">', unsafe_allow_html=True)

st.markdown("## 🪷 **Campaign Analysis** 🐝")
st.markdown("*Visualizing campaign performance and extracting actionable insights.* 🍃")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    required_cols = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing columns: {required_cols}")
        st.stop()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)
    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)

    # Filters
    st.markdown("## 🎯 Filter Your Data ✏️")
    col1, col2, col3, col4 = st.columns(4)
    platforms = ['All Platforms'] + sorted(df['platform'].dropna().unique())
    sentiments = ['All Sentiments'] + sorted(df['sentiment'].dropna().unique())
    locations = ['All Locations'] + sorted(df['location'].dropna().unique())
    media_types = ['All Media Types'] + sorted(df['media_type'].dropna().unique())
    with col1:
        selected_platform = st.selectbox("Platform", platforms)
    with col2:
        selected_sentiment = st.selectbox("Sentiment", sentiments)
    with col3:
        selected_location = st.selectbox("Location", locations)
    with col4:
        selected_media = st.selectbox("Media Type", media_types)
    col5, col6 = st.columns(2)
    with col5:
        start_date = st.date_input("Start Date", df['date'].min().date())
    with col6:
        end_date = st.date_input("End Date", df['date'].max().date())

    filtered_df = df.copy()
    if selected_platform != 'All Platforms':
        filtered_df = filtered_df[filtered_df['platform'] == selected_platform]
    if selected_sentiment != 'All Sentiments':
        filtered_df = filtered_df[filtered_df['sentiment'] == selected_sentiment]
    if selected_location != 'All Locations':
        filtered_df = filtered_df[filtered_df['location'] == selected_location]
    if selected_media != 'All Media Types':
        filtered_df = filtered_df[filtered_df['media_type'] == selected_media]
    filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date) & (filtered_df['date'].dt.date <= end_date)]

    st.markdown("### Cleaned Data Preview")
    st.dataframe(filtered_df.head())

    st.markdown("### Sentiment Breakdown 🌸")
    st.plotly_chart(px.pie(filtered_df, names='sentiment', title="Sentiment Breakdown"), use_container_width=True)
    for insight in get_top_sentiments(filtered_df):
        st.markdown(f"- {insight}")

    st.markdown("### Engagement Trend 📈")
    trend_df = filtered_df.groupby('date')['engagements'].sum().reset_index()
    fig = px.line(trend_df, x='date', y='engagements', title="Engagement Trend Over Time")
    st.plotly_chart(fig, use_container_width=True)
    for insight in get_engagement_trend_insights(filtered_df):
        st.markdown(f"- {insight}")

    st.markdown("### Platform Engagements 🧩")
    platform_df = filtered_df.groupby('platform')['engagements'].sum().reset_index()
    st.plotly_chart(px.bar(platform_df, x='platform', y='engagements', title="Platform Engagements"), use_container_width=True)
    for insight in get_platform_engagements_insights(filtered_df):
        st.markdown(f"- {insight}")

    st.markdown("### Media Type Mix 🖼️")
    st.plotly_chart(px.pie(filtered_df, names='media_type', title="Media Type Mix"), use_container_width=True)
    for insight in get_media_type_mix_insights(filtered_df):
        st.markdown(f"- {insight}")

    st.markdown("### Top Locations 📍")
    loc_df = filtered_df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).reset_index()
    st.plotly_chart(px.bar(loc_df, x='location', y='engagements', title="Top 5 Locations"), use_container_width=True)
    for insight in get_top_locations_insights(filtered_df):
        st.markdown(f"- {insight}")

    def create_pdf():
        pdf = PDFReport()
        pdf.add_page()
        pdf.chapter_title("Sentiment Insights")
        pdf.chapter_body("\n".join(get_top_sentiments(filtered_df)))
        pdf.chapter_title("Engagement Trend")
        pdf.chapter_body("\n".join(get_engagement_trend_insights(filtered_df)))
        pdf.chapter_title("Platform Insights")
        pdf.chapter_body("\n".join(get_platform_engagements_insights(filtered_df)))
        pdf.chapter_title("Media Types")
        pdf.chapter_body("\n".join(get_media_type_mix_insights(filtered_df)))
        pdf.chapter_title("Top Locations")
        pdf.chapter_body("\n".join(get_top_locations_insights(filtered_df)))
        return pdf.output(dest='S').encode('latin1')

    st.markdown("### Export Report to PDF 📄")
    if st.button("Export to PDF"):
        pdf_bytes = create_pdf()
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="dashboard_report.pdf">📥 Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; font-size:16px;'>🌸 Hope this analysis is helpful! 🐰🌼<br><small>Made by Zulfa Nur Alina Putri</small></p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

