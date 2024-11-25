import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO


#TO FIX LATER 2024-11-24 23:09:45.937 The `use_column_width` parameter has been deprecated and will be removed in a future release. Please utilize the `use_container_width` parameter instead.

# Load the data
data = pd.read_csv("E:\\extraDownloads\\jobSearch.csv")

st.title("Job Application Tracker Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
selected_medium = st.sidebar.multiselect("Application Medium", data["Application Medium"].unique())
filtered_data = data[data["Application Medium"].isin(selected_medium)] if selected_medium else data

# Metrics
total_applications = len(filtered_data)
unique_companies = filtered_data['Company'].nunique()
st.write(f"Total Applications: {total_applications}")
st.write(f"Unique Companies: {unique_companies}")

# Tabs for organizing visualizations
tabs = st.tabs(["Sankey Diagram", "Applications Over Time", "Applications by Company", "Outcome Distribution", "Success Rates"])

# Sankey Diagram
with tabs[0]:
    st.header("Sankey Diagram: Application Status Flow")
    filtered_data.loc[:, "Application Status"] = filtered_data["Application Status"].fillna("Applied")
    filtered_data.loc[:, "Post applications status"] = filtered_data["Post applications status"].fillna("Yet to Hear Back (Post Interview)")

    labels = [
        "Total Applications",
        "Applied (Yet to Hear Back)",
        "Rejected",
        "CA/PS (Initial Interview)",
        "Yet to Hear Back (Post Interview)"
    ]
    sources = []
    targets = []
    values = []

    applied_count = len(filtered_data[filtered_data["Application Status"] == "Applied"])
    rejected_count = len(filtered_data[filtered_data["Application Status"] == "Rejected"])
    ca_ps_count = len(filtered_data[filtered_data["Application Status"].isin(["CA", "Second_round"])])

    sources += [0, 0, 0]
    targets += [1, 2, 3]
    values += [applied_count, rejected_count, ca_ps_count]

    rejected_after_interview = len(filtered_data[
        (filtered_data["Application Status"].isin(["CA", "Second_round"])) &
        (filtered_data["Post applications status"] == "Rejected")
    ])
    yet_to_hear_back_after_interview = len(filtered_data[
        (filtered_data["Application Status"].isin(["CA", "Second_round"])) &
        (filtered_data["Post applications status"] == "Yet to Hear Back (Post Interview)")
    ])

    sources += [3, 3]
    targets += [2, 4]
    values += [rejected_after_interview, yet_to_hear_back_after_interview]

    fig_sankey = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values
        )
    ))

    fig_sankey.update_layout(
        width=1200,
        height=700,
        title_font_size=20,
        title="Job Application Tracker: Sankey Diagram"
    )

    st.plotly_chart(fig_sankey)

# Applications Over Time
with tabs[1]:
    st.header("Applications Over Time")
    data['Application Date'] = pd.to_datetime(data['Application Date'], errors='coerce')
    application_trends = data.groupby(data['Application Date'].dt.to_period('M')).size()
    application_trends.index = application_trends.index.to_timestamp()

    plt.figure(figsize=(10, 6))
    application_trends.plot(kind='line', marker='o', title='Applications Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Applications')
    plt.grid(True)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    st.image(buffer, caption="Applications Over Time", use_column_width=True)
    buffer.close()

# Applications by Company
with tabs[2]:
    st.header("Applications by Company")
    applications_by_company = data['Company'].value_counts().head(10)

    plt.figure(figsize=(10, 6))
    applications_by_company.plot(kind='barh', title='Applications by Company')
    plt.xlabel('Number of Applications')
    plt.ylabel('Company')
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    st.image(buffer, caption="Applications by Company", use_column_width=True)
    buffer.close()

# Outcome Distribution
with tabs[3]:
    st.header("Outcome Distribution")
    outcomes = data['Application Status'].fillna('Unknown').value_counts()

    plt.figure(figsize=(8, 8))
    outcomes.plot(kind='pie', autopct='%1.1f%%', startangle=90, title='Outcome Distribution')
    plt.ylabel('')
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    st.image(buffer, caption="Outcome Distribution", use_column_width=True)
    buffer.close()

# Success Rates by Medium
with tabs[4]:
    st.header("Success Rates by Application Medium")
    success_rates = data.groupby('Application Medium')['Application Status'].value_counts(normalize=True).unstack(fill_value=0)
    success_rates = success_rates[['CA', 'Rejected']].sort_index()

    success_rates.plot(kind='bar', stacked=True, figsize=(10, 6), title='Success Rates by Application Medium')
    plt.xlabel('Application Medium')
    plt.ylabel('Proportion')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    st.image(buffer, caption="Success Rates by Application Medium", use_column_width=True)
    buffer.close()