import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# --- Helper insight functions ---
def top_sentiments(df):
    return df['sentiment'].value_counts().head(3).items()

def engagement_trend_insights(df):
    trend = df.groupby('date')['engagements'].sum().sort_index()
    top_dates = trend.sort_values(ascending=False).head(3)
    last_change = trend.pct_change().iloc[-1] if len(trend) > 1 else 0
    insights = [(date.strftime("%Y-%m-%d"), val) for date, val in top_dates.items()]
    change_str = f"Engagements {'increased' if last_change > 0 else 'decreased'} by {abs(last_change)*100:.1f}% recently"
    return insights, change_str

def platform_engagements(df):
    return df.groupby('platform')['engagements'].sum().sort_values(ascending=False).head(3).items()

def media_type_mix(df):
    return df['media_type'].value_counts().head(3).items()

def top_locations(df):
    return df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(3).items()

# PDF generation class
class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(76, 175, 80)
        self.cell(0, 10, "Interactive Media Intelligence Dashboard Report", 0, 1, "C")

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(251, 192, 45)
        self.cell(0, 10, title, 0, 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 8, body)
        self.ln()

# --- Streamlit app config ---
st.set_page_config(page_title="Interactive Media Intelligence Dashboard", layout="wide")

# CSS for minimal professional style
st.markdown("""
<style>
    /* Base font */
    html, body, [class*="css"]  {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #3a3a3a;
        background-color: #fff;
    }
    /* Container */
    .app-container {
        max-width: 960px;
        margin: auto;
        padding: 40px 20px;
    }
    /* Headers */
    h1 {
        font-weight: 700;
        font-size: 2.8rem;
        color: #4caf50;
        margin-bottom: 0.25em;
        letter-spacing: -0.02em;
    }
    h2 {
        font-weight: 600;
        font-size: 1.6rem;
        color: #333;
        border-bottom: 2px solid #fbc02d;
        padding-bottom: 4px;
        margin-top: 3rem;
        margin-bottom: 1rem;
        letter-spacing: -0.01em;
    }
    /* Paragraphs and lists */
    p, li {
        font-size: 1rem;
        line-height: 1.6;
        color: #555;
    }
    /* Buttons */
    div.stButton > button:first-child {
        background-color: #fce4ec;
        color: #388e3c;
        border-radius: 6px;
        font-weight: 600;
        font-size: 1rem;
        padding: 10px 28px;
        border: none;
        transition: background-color 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #f8bbd0;
        color: #2e7d32;
        cursor: pointer;
    }
    /* Dataframe style */
    .dataframe {
        border-radius: 6px;
        border: 1px solid #ddd;
        margin-top: 1rem;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    /* Plotly container tweaks */
    .stPlotlyChart > div {
        margin-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Layout container
st.markdown('<div class="app-container">', unsafe_allow_html=True)

st.title("Interactive Media Intelligence Dashboard")
st.markdown("Upload a CSV file containing columns: **Date**, **Platform**, **Sentiment**, **Location**, **Engagements**, **Media Type**.")

uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    required_cols = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing columns! Found: {list(df.columns)}")
        st.stop()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)

    st.markdown("### Data Preview")
    st.dataframe(df.head())

    # Sentiment Pie Chart
    st.markdown("### Sentiment Breakdown")
    fig_sentiment = px.pie(df, names='sentiment', title='Sentiment Breakdown', color_discrete_sequence=px.colors.sequential.Greens)
    st.plotly_chart(fig_sentiment, use_container_width=True)

    st.markdown("Insights:")
    for sentiment, count in top_sentiments(df):
        st.markdown(f"- {sentiment}: {count} mentions")

    # Engagement Trend Line Chart
    st.markdown("### Engagement Trend Over Time")
    engagement_trend = df.groupby('date')['engagements'].sum().reset_index()
    fig_engagement = px.line(engagement_trend, x='date', y='engagements', title='Engagement Trend Over Time', color_discrete_sequence=['#4caf50'])
    st.plotly_chart(fig_engagement, use_container_width=True)

    insights, change_str = engagement_trend_insights(df)
    st.markdown("Insights:")
    for date, val in insights:
        st.markdown(f"- {date}: {val} engagements")
    st.markdown(f"- {change_str}")

    # Platform Engagements Bar Chart
    st.markdown("### Platform Engagements")
    platform_eng = df.groupby('platform')['engagements'].sum().sort_values(ascending=False).reset_index()
    fig_platform = px.bar(platform_eng, x='platform', y='engagements', color='platform', title='Platform Engagements', color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig_platform, use_container_width=True)

    st.markdown("Insights:")
    for platform, val in platform_engagements(df):
        st.markdown(f"- {platform}: {val} engagements")

    # Media Type Pie Chart
    st.markdown("### Media Type Mix")
    fig_media = px.pie(df, names='media_type', title='Media Type Mix', color_discrete_sequence=px.colors.sequential.Mint)
    st.plotly_chart(fig_media, use_container_width=True)

    st.markdown("Insights:")
    for media, count in media_type_mix(df):
        st.markdown(f"- {media}: {count} entries")

    # Top Locations Bar Chart
    st.markdown("### Top 5 Locations by Engagements")
    top_locs = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).reset_index()
    fig_locs = px.bar(top_locs, x='location', y='engagements', color='location', title='Top 5 Locations by Engagements', color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig_locs, use_container_width=True)

    st.markdown("Insights:")
    for location, val in top_locations(df):
        st.markdown(f"- {location}: {val} engagements")

    # Strategy Ideas
    st.markdown("### Strategy Ideas")
    st.markdown(
        """
        - Prioritize high-engagement platforms and media types for campaign focus.  
        - Leverage positive sentiment periods to amplify messaging.  
        - Target key locations with geo-specific marketing efforts.  
        - Address dips in engagement with tailored content or promotions.  
        """
    )

    # PDF generation
    def generate_pdf():
        pdf = PDF()
        pdf.add_page()

        pdf.chapter_title("Sentiment Breakdown Insights")
        pdf.chapter_body("\n".join([f"{sent}: {cnt}" for sent, cnt in top_sentiments(df)]))

        pdf.chapter_title("Engagement Trend Insights")
        pdf.chapter_body("\n".join([f"{date}: {val}" for date, val in insights]))
        pdf.chapter_body(change_str)

        pdf.chapter_title("Platform Engagements")
        pdf.chapter_body("\n".join([f"{plat}: {val}" for plat, val in platform_engagements(df)]))

        pdf.chapter_title("Media Type Mix")
        pdf.chapter_body("\n".join([f"{media}: {cnt}" for media, cnt in media_type_mix(df)]))

        pdf.chapter_title("Top Locations")
        pdf.chapter_body("\n".join([f"{loc}: {val}" for loc, val in top_locations(df)]))

        pdf.chapter_title("Strategy Ideas")
        pdf.chapter_body(
            "- Prioritize high-engagement platforms and media types for campaign focus.\n"
            "- Leverage positive sentiment periods to amplify messaging.\n"
            "- Target key locations with geo-specific marketing efforts.\n"
            "- Address dips in engagement with tailored content or promotions."
        )

        return pdf.output(dest='S').encode('latin1')

    st.markdown("### Download Report")
    if st.button("Generate PDF Report"):
        pdf_data = generate_pdf()
        b64_pdf = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="media_dashboard_report.pdf" style="font-weight:bold; color:#4caf50;">📥 Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)

st.markdown('<p style="font-size:1.1rem; font-weight:600; color:#a5d6d6; margin-top:3rem;">Hope it helps! ^^</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
