from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Page setup
st.set_page_config(
    page_title="Citi Group Data Governance Dashboard",
    page_icon="favicon.ico",
    layout="centered"
)

# HEADER & LOGO CENTERED
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.image("favicon.ico", width=60)
    st.markdown("## **Citi Group Data Quality Dashboard**")
    st.markdown("*Simulation of data governance framework and rule monitoring for financial domain.*")
    st.markdown("---")

# Fetch from Supabase
response = supabase.table("dq_log").select("*").execute()
df = pd.DataFrame(response.data)

# Make sure date format is correct
df["run_date"] = pd.to_datetime(df["run_date"])

# Sidebar filter
st.sidebar.title("🔎 Filters")
selected_run = st.sidebar.selectbox("Select Run Date", sorted(df["run_date"].unique(), reverse=True))
selected_df = df[df["run_date"] == selected_run]

# KPI cards
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

# Accuracy by domain
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

# Trend over time
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

# Table with conditional formatting
def color_status(row):
    acc = row["accuracy_pct"]
    if acc >= 95:
        return ['background-color: #d4edda; color: #155724'] * len(row)
    elif acc >= 92.5:
        return ['background-color: #fff3cd; color: #856404'] * len(row)
    else:
        return ['background-color: #f8d7da; color: #721c24'] * len(row)

styled_df = selected_df.style.apply(color_status, axis=1)
st.markdown("### 🧾 Validation Rule Details")
st.dataframe(styled_df, use_container_width=True)

# OPTIONAL: Seed data once (run only if needed)
def seed_supabase_with_dummy_data():
    domains = ['loan', 'customer', 'risk', 'investment', 'kyc']
    np.random.seed(42)
    for i in range(10):
        run_date = datetime(2025, 4, 1) + pd.Timedelta(days=i * 2)
        for domain in domains:
            total = np.random.randint(4000, 6000)
            failed = np.random.randint(0, 300)
            accuracy = round(100 * (total - failed) / total, 2)

            supabase.table("dq_log").insert({
                "run_date": run_date.isoformat(),
                "domain": domain,
                "accuracy_pct": accuracy,
                "rules_checked": total,
                "failed_rules": failed
            }).execute()

# Uncomment this only once if you want to populate dummy data:
# seed_supabase_with_dummy_data()
