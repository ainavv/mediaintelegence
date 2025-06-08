import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import io

# --- Theme colors & fonts for cottage flowery vibe ---
PRIMARY_COLOR = "#A7C7E7"  # soft blue
SECONDARY_COLOR = "#F6E2B3"  # soft yellow
ACCENT_COLOR = "#D9A5B3"  # dusty rose
BG_COLOR = "#FFF9F4"  # cream background
FONT_FAMILY = "Georgia, serif"

REQUIRED_COLUMNS = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media type']

def style():
    st.markdown(
        f"""
        <style>
        .reportview-container {{
            background-color: {BG_COLOR};
            font-family: {FONT_FAMILY};
        }}
        .sidebar .sidebar-content {{
            background-color: {SECONDARY_COLOR};
            font-family: {FONT_FAMILY};
        }}
        h1, h2, h3, h4 {{
            color: {ACCENT_COLOR};
            font-family: {FONT_FAMILY};
        }}
        .stButton>button {{
            background-color: {ACCENT_COLOR};
            color: white;
            font-weight: bold;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def validate_columns(df):
    cols = [c.strip().lower() for c in df.columns]
    missing = [col for col in REQUIRED_COLUMNS if col not in cols]
    return missing, cols

def clean_data(df):
    df.columns = df.columns.str.strip().str.lower()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)
    for col in ['platform', 'sentiment', 'location', 'media type']:
        df[col] = df[col].astype(str).str.strip()
    return df

def get_top_insights_sentiment(df):
    counts = df['sentiment'].value_counts().head(3)
    return [f"{i+1}. {idx} sentiment appears {val} times" for i, (idx, val) in enumerate(counts.items())]

def get_top_insights_engagement_trend(df):
    monthly = df.groupby(pd.Grouper(key='date', freq='M'))['engagements'].sum()
    top_months = monthly.sort_values(ascending=False).head(3)
    return [f"{i+1}. {d.strftime('%b %Y')} has {val} engagements" for i, (d, val) in enumerate(top_months.items())]

def get_top_insights_platform(df):
    platform_sum = df.groupby('platform')['engagements'].sum().sort_values(ascending=False).head(3)
    return [f"{i+1}. Platform '{idx}' has {val} total engagements" for i, (idx, val) in enumerate(platform_sum.items())]

def get_top_insights_media_type(df):
    media_counts = df['media type'].value_counts().head(3)
    return [f"{i+1}. Media Type '{idx}' appears {val} times" for i, (idx, val) in enumerate(media_counts.items())]

def get_top_insights_location(df):
    loc_sum = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(3)
    return [f"{i+1}. Location '{idx}' has {val} total engagements" for i, (idx, val) in enumerate(loc_sum.items())]

def generate_pdf(summary_texts, insights, filename="Media_Intelligence_Summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", 'B', 18)
    pdf.set_text_color(217, 165, 179)  # dusty rose
    pdf.cell(0, 10, "🌸 Media Intelligence Dashboard Summary 🌸", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Times", '', 12)
    for section, texts in summary_texts.items():
        pdf.set_text_color(167, 199, 231)  # soft blue
        pdf.cell(0, 10, section, ln=True)
        pdf.set_text_color(0, 0, 0)
        for line in texts:
            pdf.multi_cell(0, 8, line)
        pdf.ln(5)

    pdf.set_text_color(217, 165, 179)
    pdf.cell(0, 10, "Campaign Strategy Summary", ln=True)
    pdf.set_text_color(0, 0, 0)
    for line in insights:
        pdf.multi_cell(0, 8, line)

    pdf.ln(10)
    pdf.set_font("Times", 'I', 12)
    pdf.cell(0, 10, "Thank you for using the Interactive Media Intelligence Dashboard. Hope this helps your campaign strategy!", ln=True, align='C')

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

def main():
    st.set_page_config(page_title="Interactive Media Intelligence Dashboard", layout="wide", page_icon="🌸")
    style()

    st.title("🌸 Interactive Media Intelligence Dashboard 🌸")
    st.markdown("### Step 1: Upload CSV File with columns: Date, Platform, Sentiment, Location, Engagements, Media Type")

    uploaded_file = st.file_uploader("Upload CSV file here", type=['csv'])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='latin1')
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")
            return

        missing_cols, cols = validate_columns(df)
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            st.write("Detected columns:", cols)
            return

        st.markdown("### Step 2: Clean Data")
        df = clean_data(df)
        st.write("Sample cleaned data:")
        st.dataframe(df.head())

        st.markdown("### Step 3: Visualizations")

        st.markdown("#### Sentiment Breakdown")
        fig1 = px.pie(df, names='sentiment', title="Sentiment Breakdown", color_discrete_sequence=px.colors.sequential.Rose)
        st.plotly_chart(fig1, use_container_width=True)
        sentiment_insights = get_top_insights_sentiment(df)
        st.markdown("**Top 3 Sentiment Insights:**")
        for insight in sentiment_insights:
            st.write("- " + insight)

        st.markdown("#### Engagement Trend Over Time")
        engagement_time = df.groupby('date')['engagements'].sum().reset_index()
        fig2 = px.line(engagement_time, x='date', y='engagements',
                       title="Engagements Over Time",
                       markers=True,
                       color_discrete_sequence=[ACCENT_COLOR])
        st.plotly_chart(fig2, use_container_width=True)
        engagement_insights = get_top_insights_engagement_trend(df)
        st.markdown("**Top 3 Engagement Trend Insights:**")
        for insight in engagement_insights:
            st.write("- " + insight)

        st.markdown("#### Platform Engagements")
        platform_eng = df.groupby('platform')['engagements'].sum().reset_index().sort_values(by='engagements', ascending=False)
        fig3 = px.bar(platform_eng, x='platform', y='engagements',
                      title="Platform Engagements",
                      color='engagements',
                      color_continuous_scale='Pinkyl')
        st.plotly_chart(fig3, use_container_width=True)
        platform_insights = get_top_insights_platform(df)
        st.markdown("**Top 3 Platform Insights:**")
        for insight in platform_insights:
            st.write("- " + insight)

        st.markdown("#### Media Type Mix")
        fig4 = px.pie(df, names='media type', title="Media Type Mix", color_discrete_sequence=px.colors.sequential.Pinkyl)
        st.plotly_chart(fig4, use_container_width=True)
        media_insights = get_top_insights_media_type(df)
        st.markdown("**Top 3 Media Type Insights:**")
        for insight in media_insights:
            st.write("- " + insight)

        st.markdown("#### Top 5 Locations by Engagements")
        top_loc = df.groupby('location')['engagements'].sum().reset_index().sort_values(by='engagements', ascending=False).head(5)
        fig5 = px.bar(top_loc, x='location', y='engagements',
                      title="Top 5 Locations by Engagements",
                      color='engagements',
                      color_continuous_scale='RdPu')
        st.plotly_chart(fig5, use_container_width=True)
        location_insights = get_top_insights_location(df)
        st.markdown("**Top 3 Location Insights:**")
        for insight in location_insights:
            st.write("- " + insight)

        # Step 4: Campaign Strategy Summary (simple text based on data)
        st.markdown("### Step 4: Campaign Strategy Summary")
        strategy_points = [
            "1. Focus on boosting positive sentiment channels to enhance brand reputation.",
            "2. Optimize campaign timing during months with highest engagement trends.",
            "3. Prioritize platforms with highest engagement for targeted ad spend.",
            "4. Diversify media types but emphasize those with highest audience reach.",
            "5. Allocate resources strategically to top-performing locations."
        ]
        for point in strategy_points:
            st.write(point)

        # Step 5: Download as PDF
        st.markdown("### Step 5: Download Summary as PDF")
        summary_texts = {
            "Sentiment Insights": sentiment_insights,
            "Engagement Trend Insights": engagement_insights,
            "Platform Insights": platform_insights,
            "Media Type Insights": media_insights,
            "Location Insights": location_insights,
        }
        pdf_file = generate_pdf(summary_texts, strategy_points)

        st.download_button(
            label="📥 Download PDF Summary",
            data=pdf_file,
            file_name="Media_Intelligence_Summary.pdf",
            mime="application/pdf"
        )

        # Step 6: Closing statement
        st.markdown("### Thank you!")
        st.info("Thank you for using the Interactive Media Intelligence Dashboard. Hope this helps your campaign strategy! 🌸")

    else:
        st.info("Please upload a CSV file to proceed.")

if __name__ == "__main__":
    main()

