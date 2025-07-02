import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io

st.set_page_config(page_title="Auto Dashboard", layout="wide")

st.title("📊 Streamlit Auto Dashboard Generator")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

# --- Process File ---
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    # Try parsing datetime
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            continue

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # --- Column Type Detection ---
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    st.markdown("---")
    st.subheader("🎛️ Optional Filters")

    # --- Category Filter ---
    if categorical_cols:
        cat_filter_col = st.selectbox("Filter by category column", categorical_cols)
        cat_options = df[cat_filter_col].dropna().unique()
        selected_cats = st.multiselect("Select category values", options=cat_options)
        if selected_cats:
            df = df[df[cat_filter_col].isin(selected_cats)]

    # --- Numeric Filter ---
    if numeric_cols:
        num_filter_col = st.selectbox("Filter by numeric column", numeric_cols)
        min_val = float(df[num_filter_col].min())
        max_val = float(df[num_filter_col].max())
        val_range = st.slider("Select value range", min_val, max_val, (min_val, max_val))
        df = df[(df[num_filter_col] >= val_range[0]) & (df[num_filter_col] <= val_range[1])]

    st.markdown("---")
    st.subheader("📊 Auto-Generated Charts")

    # --- Histogram ---
    if numeric_cols:
        hist_col = st.selectbox("Select column for Histogram", numeric_cols)
        fig1 = px.histogram(df, x=hist_col, title=f"Histogram of {hist_col}")
        st.plotly_chart(fig1, use_container_width=True)

    # --- Pie Chart ---
    if categorical_cols:
        pie_col = st.selectbox("Select column for Pie Chart", categorical_cols)
        fig2 = px.pie(df, names=pie_col, title=f"Pie Chart of {pie_col}")
        st.plotly_chart(fig2, use_container_width=True)

    # --- Line Chart ---
    if date_cols and numeric_cols:
        date_col = st.selectbox("Select date column", date_cols)
        y_col = st.selectbox("Select numeric column for Line Chart", numeric_cols)
        df_sorted = df.sort_values(date_col)
        fig3 = px.line(df_sorted, x=date_col, y=y_col, title=f"{y_col} over {date_col}")
        st.plotly_chart(fig3, use_container_width=True)

    # --- Export Section ---
    st.markdown("---")
    st.subheader("📤 Export Options")

    # CSV Export
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Filtered Data as CSV", csv_data, "filtered_data.csv", "text/csv")

    # PDF Export
    if st.button("⬇️ Download Summary as PDF"):
        summary = df.describe().round(2).to_string()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 10, f"Data Summary\n\n{summary}")
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        st.download_button("Download PDF", pdf_output, file_name="data_summary.pdf", mime="application/pdf")
