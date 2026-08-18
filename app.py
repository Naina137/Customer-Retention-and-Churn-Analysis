import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Customer Retention & Churn Analysis",
    page_icon="",
    layout="wide"
)

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    file_path = "WA_Fn-UseC_-Telco-Customer-Churn.csv"

    df = pd.read_csv(file_path)

    # Convert TotalCharges to numeric
    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"], errors="coerce"
    )

    # Remove rows where important numeric value is missing
    df = df.dropna(subset=["TotalCharges"])

    return df


try:
    df = load_data()
except Exception as e:
    st.error("Unable to load the customer churn dataset.")
    st.error(str(e))
    st.stop()


# -----------------------------
# Title
# -----------------------------
st.title("Customer Retention & Churn Analysis")
st.write(
    "Interactive analysis of customer churn, retention patterns, "
    "customer behaviour and customer lifetime metrics."
)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

contract_filter = st.sidebar.multiselect(
    "Contract Type",
    options=sorted(df["Contract"].unique()),
    default=sorted(df["Contract"].unique())
)

internet_filter = st.sidebar.multiselect(
    "Internet Service",
    options=sorted(df["InternetService"].unique()),
    default=sorted(df["InternetService"].unique())
)

payment_filter = st.sidebar.multiselect(
    "Payment Method",
    options=sorted(df["PaymentMethod"].unique()),
    default=sorted(df["PaymentMethod"].unique())
)

filtered_df = df[
    (df["Contract"].isin(contract_filter)) &
    (df["InternetService"].isin(internet_filter)) &
    (df["PaymentMethod"].isin(payment_filter))
]


# -----------------------------
# KPI Calculations
# -----------------------------
total_customers = len(filtered_df)

churned_customers = (
    filtered_df["Churn"] == "Yes"
).sum()

retained_customers = (
    filtered_df["Churn"] == "No"
).sum()

churn_rate = (
    churned_customers / total_customers * 100
    if total_customers > 0 else 0
)

avg_monthly_charges = (
    filtered_df["MonthlyCharges"].mean()
    if total_customers > 0 else 0
)

avg_tenure = (
    filtered_df["tenure"].mean()
    if total_customers > 0 else 0
)


# -----------------------------
# KPI Cards
# -----------------------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Customers",
    f"{total_customers:,}"
)

col2.metric(
    "Churned Customers",
    f"{churned_customers:,}"
)

col3.metric(
    "Retained Customers",
    f"{retained_customers:,}"
)

col4.metric(
    "Churn Rate",
    f"{churn_rate:.2f}%"
)

col5.metric(
    "Average Tenure",
    f"{avg_tenure:.1f} months"
)


st.divider()


# -----------------------------
# Churn Overview
# -----------------------------
st.subheader("Churn Overview")

col1, col2 = st.columns(2)

with col1:
    churn_count = (
        filtered_df["Churn"]
        .value_counts()
        .reset_index()
    )

    churn_count.columns = ["Churn", "Customers"]

    fig = px.pie(
        churn_count,
        names="Churn",
        values="Customers",
        hole=0.45,
        title="Customer Churn Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:
    contract_churn = pd.crosstab(
        filtered_df["Contract"],
        filtered_df["Churn"],
        normalize="index"
    ).reset_index()

    if "Yes" in contract_churn.columns:
        contract_churn["Churn Rate"] = (
            contract_churn["Yes"] * 100
        )

        fig = px.bar(
            contract_churn,
            x="Contract",
            y="Churn Rate",
            title="Churn Rate by Contract Type",
            labels={
                "Churn Rate": "Churn Rate (%)"
            },
            text_auto=".1f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# -----------------------------
# Contract Analysis
# -----------------------------
st.subheader("Customer Retention by Contract")

contract_data = (
    filtered_df.groupby(
        ["Contract", "Churn"]
    )
    .size()
    .reset_index(name="Customers")
)

fig = px.bar(
    contract_data,
    x="Contract",
    y="Customers",
    color="Churn",
    barmode="group",
    title="Customers by Contract and Churn Status"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# Tenure Analysis
# -----------------------------
st.subheader("Tenure Analysis")

fig = px.histogram(
    filtered_df,
    x="tenure",
    color="Churn",
    nbins=30,
    barmode="overlay",
    title="Customer Tenure Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# Monthly Charges vs Churn
# -----------------------------
st.subheader("Monthly Charges and Churn")

fig = px.box(
    filtered_df,
    x="Churn",
    y="MonthlyCharges",
    color="Churn",
    title="Monthly Charges by Churn Status"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# Internet Service Analysis
# -----------------------------
st.subheader("Internet Service Analysis")

internet_data = (
    pd.crosstab(
        filtered_df["InternetService"],
        filtered_df["Churn"],
        normalize="index"
    ) * 100
).reset_index()

if "Yes" in internet_data.columns:
    internet_data = internet_data.rename(
        columns={"Yes": "Churn Rate"}
    )

    fig = px.bar(
        internet_data,
        x="InternetService",
        y="Churn Rate",
        title="Churn Rate by Internet Service",
        text_auto=".1f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# -----------------------------
# Payment Method Analysis
# -----------------------------
st.subheader("Payment Method Analysis")

payment_data = (
    pd.crosstab(
        filtered_df["PaymentMethod"],
        filtered_df["Churn"],
        normalize="index"
    ) * 100
).reset_index()

if "Yes" in payment_data.columns:
    payment_data = payment_data.rename(
        columns={"Yes": "Churn Rate"}
    )

    fig = px.bar(
        payment_data,
        x="PaymentMethod",
        y="Churn Rate",
        title="Churn Rate by Payment Method",
        text_auto=".1f"
    )

    fig.update_layout(
        xaxis_tickangle=-30
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# -----------------------------
# Senior Citizen Analysis
# -----------------------------
st.subheader("Customer Demographic Analysis")

senior_data = (
    filtered_df.groupby(
        ["SeniorCitizen", "Churn"]
    )
    .size()
    .reset_index(name="Customers")
)

senior_data["Customer Group"] = senior_data[
    "SeniorCitizen"
].map({
    0: "Non-Senior Citizen",
    1: "Senior Citizen"
})

fig = px.bar(
    senior_data,
    x="Customer Group",
    y="Customers",
    color="Churn",
    barmode="group",
    title="Churn by Customer Demographic"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# Customer Lifetime Value
# -----------------------------
st.subheader("Customer Lifetime Value Analysis")

filtered_df["EstimatedLifetimeValue"] = (
    filtered_df["MonthlyCharges"] *
    filtered_df["tenure"]
)

avg_lifetime_value = (
    filtered_df["EstimatedLifetimeValue"].mean()
    if len(filtered_df) > 0 else 0
)

st.metric(
    "Average Estimated Customer Lifetime Value",
    f"${avg_lifetime_value:,.2f}"
)

fig = px.scatter(
    filtered_df,
    x="tenure",
    y="MonthlyCharges",
    color="Churn",
    size="EstimatedLifetimeValue",
    hover_data=[
        "Contract",
        "InternetService",
        "PaymentMethod"
    ],
    title="Customer Lifetime Value Relationship"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# Churn Drivers
# -----------------------------
st.subheader("Key Churn Drivers")

churn_summary = {}

for column in [
    "Contract",
    "InternetService",
    "PaymentMethod",
    "TechSupport",
    "OnlineSecurity"
]:

    temp = (
        pd.crosstab(
            filtered_df[column],
            filtered_df["Churn"],
            normalize="index"
        ) * 100
    )

    if "Yes" in temp.columns:
        churn_summary[column] = temp["Yes"].max()


driver_df = pd.DataFrame(
    list(churn_summary.items()),
    columns=["Feature", "Highest Churn Rate"]
)

fig = px.bar(
    driver_df,
    x="Feature",
    y="Highest Churn Rate",
    title="Maximum Churn Rate Across Key Customer Features",
    text_auto=".1f"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# Business Insights
# -----------------------------
st.subheader("Business Insights")

if churn_rate > 25:
    st.write(
        "The overall churn rate is relatively high. "
        "The business should focus on targeted retention campaigns."
    )
else:
    st.write(
        "The overall churn rate is moderate. "
        "Retention strategies should focus on high-risk customer groups."
    )

if "Month-to-month" in filtered_df["Contract"].values:
    month_customers = filtered_df[
        filtered_df["Contract"] == "Month-to-month"
    ]

    if len(month_customers) > 0:
        month_churn = (
            month_customers["Churn"] == "Yes"
        ).mean() * 100

        st.write(
            f"Month-to-month customers show a churn rate of "
            f"{month_churn:.2f}%, indicating higher retention risk."
        )

if len(filtered_df) > 0:
    high_charge_churn = filtered_df[
        filtered_df["Churn"] == "Yes"
    ]["MonthlyCharges"].mean()

    st.write(
        f"Average monthly charges among churned customers are "
        f"${high_charge_churn:.2f}."
    )

st.write(
    "Recommended actions include targeted retention offers, "
    "long-term contract incentives, improved customer support, "
    "and proactive engagement with high-risk customers."
)


# -----------------------------
# Data Preview
# -----------------------------
st.subheader("Filtered Customer Data")

st.dataframe(
    filtered_df.head(100),
    use_container_width=True
)


# -----------------------------
# Download Data
# -----------------------------
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Customer Data",
    data=csv_data,
    file_name="filtered_customer_churn.csv",
    mime="text/csv"
)


# -----------------------------
# Footer
# -----------------------------
st.divider()

st.caption(
    "Customer Retention & Churn Analysis | Data Science & Analytics"
)