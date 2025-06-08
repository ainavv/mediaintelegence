import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# --- Helper functions for insights ---
def get_top_sentiments(df):
    counts = df['sentiment'].value_counts().head(3)
    return [f"{sentiment}: {count}" for sentiment, count in counts.items()]

def get_engagement_trend_insights(df):
    trend = df.groupby('date')['engagements'].sum()
    increase = trend.pct_change().fillna(0)
    top_dates = trend.sort_values(ascending=False).head(3)
    insights = [f"Highest engagement on {date.strftime('%Y-%m-%d')}: {val}" for date, val in top_dates.items()]
    if increase.iloc[-1] > 0:
        insights.append(f"Engagements increased by {increase.iloc[-1]*100:.2f}% recently")
    else:
        insights.append(f"Engagements decreased by {abs(increase.iloc[-1]*100):.2f}% recently")
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

# --- PDF generation helper ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Interactive Media Intelligence Dashboard Report', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(255, 228, 225)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, body)
        self.ln()

# --- Streamlit UI and logic ---
st.set_page_config(
    page_title="🌸 Interactive Media Intelligence Dashboard 🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

page_bg = """
<style>
    body {
        background-image: url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1470&q=80");
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        color: #6b4c3b;
    }
    .stButton>button {
        background-color: #f7c5cc;
        color: #6b4c3b;
        border-radius: 12px;
        padding: 8px 18px;
        font-weight: bold;
        font-size: 16px;
    }
    h1, h2, h3, h4 {
        color: #a04e4e;
    }
    .stMarkdown h1 {
        font-size: 2.5rem;
        font-weight: 800;
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

st.markdown("# 🌸 Interactive Media Intelligence Dashboard 🌸")
st.markdown("Upload your CSV file to begin your media insights journey! ✨🌼")

uploaded_file = st.file_uploader(
    "Upload CSV file (Date, Platform, Sentiment, Location, Engagements, Media Type) 📁",
    type=["csv"]
)

if uploaded_file:
    st.markdown("## Step 1 & 2: Data Cleaning and Normalization 🧹")
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    required_cols = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV missing required columns. Found columns: {list(df.columns)}")
        st.stop()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if df['date'].isnull().any():
        st.warning("Some dates could not be parsed and will be dropped.")
        df = df.dropna(subset=['date'])

    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)

    st.success("Data cleaned successfully! Here's a preview:")
    st.dataframe(df.head())

    st.markdown("## Step 3: Interactive Charts 📊")

    # Sentiment Pie
    st.markdown("### Sentiment Breakdown 🥧")
    fig_sentiment = px.pie(df, names='sentiment', title="Sentiment Breakdown", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_sentiment, use_container_width=True)
    insights_sentiment = get_top_sentiments(df)
    st.markdown("**Top 3 Sentiment Insights:**")
    for insight in insights_sentiment:
        st.markdown(f"- {insight}")

    # Engagement trend line chart
    st.markdown("### Engagement Trend Over Time 📈")
    df_sorted = df.sort_values('date')
    engagement_trend = df_sorted.groupby('date')['engagements'].sum().reset_index()
    fig_engagement = px.line(engagement_trend, x='date', y='engagements', title="Engagement Trend Over Time", line_shape='spline', markers=True)
    st.plotly_chart(fig_engagement, use_container_width=True)
    insights_engagement = get_engagement_trend_insights(df)
    st.markdown("**Top 3 Engagement Trend Insights:**")
    for insight in insights_engagement:
        st.markdown(f"- {insight}")

    # Platform engagement bar chart
    st.markdown("### Platform Engagements 📊")
    platform_engagement = df.groupby('platform')['engagements'].sum().reset_index().sort_values('engagements', ascending=False)
    fig_platform = px.bar(platform_engagement, x='platform', y='engagements', title="Platform Engagements", color='platform', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_platform, use_container_width=True)
    insights_platform = get_platform_engagements_insights(df)
    st.markdown("**Top 3 Platform Engagement Insights:**")
    for insight in insights_platform:
        st.markdown(f"- {insight}")

    # Media type pie chart
    st.markdown("### Media Type Mix 🥧")
    fig_media = px.pie(df, names='media_type', title="Media Type Mix", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_media, use_container_width=True)
    insights_media = get_media_type_mix_insights(df)
    st.markdown("**Top 3 Media Type Insights:**")
    for insight in insights_media:
        st.markdown(f"- {insight}")

    # Top 5 locations bar chart
    st.markdown("### Top 5 Locations by Engagements 📍")
    top_locations = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).reset_index()
    fig_location = px.bar(top_locations, x='location', y='engagements', title="Top 5 Locations by Engagements", color='location', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_location, use_container_width=True)
    insights_location = get_top_locations_insights(df)
    st.markdown("**Top 3 Location Insights:**")
    for insight in insights_location:
        st.markdown(f"- {insight}")

    # Step 8: Strategy ideas
    st.markdown("## Step 8: Strategy Ideas 💡")
    summary_text = """
    - Focus on platforms and media types generating the highest engagements to maximize ROI.
    - Monitor sentiment trends closely and tailor content to improve positive sentiment.
    - Target top-performing locations with geo-focused campaigns.
    - Increase engagement during dates with historically lower interactions using special content or promotions.
    """
    st.markdown(summary_text)

    # Step 9: Closing statement
    st.markdown("## Closing Statement ✨")
    st.markdown("Hope it helps ^^ 🌸🌼")

    # Step 7: PDF download
    st.markdown("## Download Report as PDF 📥")

    def create_pdf():
        pdf = PDFReport()
        pdf.add_page()
        pdf.chapter_title("Interactive Media Intelligence Dashboard Report")
        pdf.chapter_body("This report summarizes the data insights and visualizations generated.")

        pdf.chapter_title("Sentiment Breakdown Insights")
        pdf.chapter_body("\n".join(insights_sentiment))

        pdf.chapter_title("Engagement Trend Insights")
        pdf.chapter_body("\n".join(insights_engagement))

        pdf.chapter_title("Platform Engagement Insights")
        pdf.chapter_body("\n".join(insights_platform))

        pdf.chapter_title("Media Type Insights")
        pdf.chapter_body("\n".join(insights_media))

        pdf.chapter_title("Top Locations Insights")
        pdf.chapter_body("\n".join(insights_location))

        pdf.chapter_title("Strategy Ideas")
        pdf.chapter_body(summary_text)

        pdf.chapter_title("Closing Statement")
        pdf.chapter_body("Hope it helps ^^ 🌸🌼")

        return pdf.output(dest='S').encode('latin1')

    if st.button("Generate PDF Report"):
        pdf_bytes = create_pdf()
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="media_dashboard_report.pdf">📥 Click here to download your PDF report</a>'
        st.markdown(href, unsafe_allow_html=True)
