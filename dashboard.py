from supabase import create_client
from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Load .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit Page Setup
st.set_page_config(
    page_title="Citi Group Data Governance Dashboard",
    page_icon="favicon.ico",
    layout="wide"
)

# Header Centered
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.image("favicon.ico", width=60)
    st.markdown("## **Citi Group Data Quality Dashboard**")
    st.markdown("*Simulation of data governance framework and rule monitoring for financial domain.*")
    st.markdown("---")

# Load Data with cache timeout (fresh every 60s)
# Manual refresh
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

def load_data():
    response = supabase.table("dq_log").select("*").execute()
    return pd.DataFrame(response.data)

df = load_data()
# Format date
df["run_date"] = pd.to_datetime(df["run_date"])

# Sidebar Filters
st.sidebar.title("🔎 Filters")
selected_run = st.sidebar.selectbox("Select Run Date", sorted(df["run_date"].unique(), reverse=True))
selected_df = df[df["run_date"] == selected_run]

# KPI Cards
avg_accuracy = selected_df["accuracy_pct"].mean()
failed_rules = selected_df["failed_rules"].sum()
total_rules = selected_df["rules_checked"].sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("✅ Avg Accuracy", f"{avg_accuracy:.2f}%")
with col2:
    st.metric("❌ Failed Rules", failed_rules)
with col3:
    st.metric("📊 Total Rules Checked", total_rules)

st.markdown("---")

# Accuracy by Domain
domain_acc = selected_df.groupby("domain")["accuracy_pct"].mean().reset_index()
fig_bar = px.bar(
    domain_acc,
    x="domain",
    y="accuracy_pct",
    color="accuracy_pct",
    color_continuous_scale="Blues",
    title="Accuracy by Data Domain"
)
fig_bar.add_hline(y=95, line_dash="dot", line_color="red")
st.plotly_chart(fig_bar, use_container_width=True)

# Trend Over Time
trend = df.groupby(["run_date", "domain"])["accuracy_pct"].mean().reset_index()
fig_line = px.line(
    trend,
    x="run_date",
    y="accuracy_pct",
    color="domain",
    markers=True,
    title="Accuracy Trend Over Time"
)
fig_line.add_hline(y=95, line_dash="dot", line_color="red")
st.plotly_chart(fig_line, use_container_width=True)

# Conditional Table
def color_status(row):
    acc = row["accuracy_pct"]
    if acc >= 95:
        return ['background-color: #d4edda; color: #155724'] * len(row)
    elif acc >= 92.5:
        return ['background-color: #fff3cd; color: #856404'] * len(row)
    else:
        return ['background-color: #f8d7da; color: #721c24'] * len(row)

styled_df = selected_df.style.apply(color_status, axis=1)
st.markdown("### Validation Rule Details")
st.dataframe(styled_df, use_container_width=True)
