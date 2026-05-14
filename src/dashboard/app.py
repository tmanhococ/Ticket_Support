import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import streamlit.components.v1 as components

# Epic 11: Import internal modules for simulation and S3
from src.simulator.generator import generate_ticket, generate_drift_ticket
from src.api.utils.s3_client import get_s3_client

# Try MLflow for Model tab
try:
    from mlflow.tracking import MlflowClient
except ImportError:
    MlflowClient = None

# Page Config
st.set_page_config(page_title="Ticket Triage Operations", page_icon="🎫", layout="wide")
st.title("🎫 Ticket Triage MLOps Dashboard")


# -----------------------------------------------------------------------------
# Configuration & Setup
# -----------------------------------------------------------------------------
@st.cache_resource
def get_db_engine():
    db_url = os.getenv("DATABASE_URL", "postgresql://tickets_user:tickets_pass@db:5432/tickets_db")
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")
    engine = create_engine(db_url, pool_size=10, max_overflow=5)
    return engine


def fetch_latest_tickets(engine, limit=1000):
    query = f"SELECT * FROM tickets ORDER BY timestamp DESC LIMIT {limit}"
    df = pd.read_sql(query, engine)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


engine = get_db_engine()

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Real-time Monitoring", "📈 Drift Report", "🤖 Models", "🧪 Simulation"]
)

# =============================================================================
# Tab 1: Real-time Monitoring
# =============================================================================
with tab1:
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()

    try:
        df = fetch_latest_tickets(engine, limit=1000)

        if df.empty:
            st.info(
                "No tickets found in the database. Head to the Simulation tab to generate traffic."
            )
        else:
            # Layout for charts
            c1, c2 = st.columns([2, 1])

            with c1:
                st.subheader("Ticket Volume & Priority Spikes")
                # Time-series trend grouped by 5 minutes and priority
                df_trend = df.copy()
                df_trend.set_index("timestamp", inplace=True)
                # Fill missing predicted_priority with 'unknown'
                df_trend["predicted_priority"] = df_trend["predicted_priority"].fillna("unknown")

                # Resample by 5 min
                trend = (
                    df_trend.groupby("predicted_priority")
                    .resample("5min")
                    .size()
                    .reset_index(name="count")
                )

                fig_trend = px.area(
                    trend,
                    x="timestamp",
                    y="count",
                    color="predicted_priority",
                    title="Incoming Tickets over Time",
                    color_discrete_map={
                        "high": "red",
                        "medium": "orange",
                        "low": "green",
                        "unknown": "gray",
                    },
                )
                st.plotly_chart(fig_trend, use_container_width=True)

            with c2:
                st.subheader("Overall Priority Distribution")
                dist = df["predicted_priority"].fillna("unknown").value_counts().reset_index()
                dist.columns = ["Priority", "Count"]
                fig_pie = px.pie(
                    dist,
                    names="Priority",
                    values="Count",
                    color="Priority",
                    color_discrete_map={
                        "high": "red",
                        "medium": "orange",
                        "low": "green",
                        "unknown": "gray",
                    },
                    hole=0.4,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            st.subheader("Recent Tickets Log")
            st.dataframe(df.head(100), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Failed to fetch monitoring data: {e}")

# =============================================================================
# Tab 2: Drift Report
# =============================================================================
with tab2:
    st.subheader("Latest EvidentlyAI Data Drift Report")
    st.markdown(
        "This report compares the latest production data against the baseline "
        "to detect concept/data drift."
    )

    bucket = os.getenv("S3_BUCKET_NAME")
    object_key = "drift_reports/latest_drift_report.html"

    if st.button("Fetch Latest Report"):
        if not bucket:
            st.error("S3_BUCKET_NAME is not configured.")
        else:
            try:
                s3 = get_s3_client()
                response = s3.get_object(Bucket=bucket, Key=object_key)
                html_content = response["Body"].read().decode("utf-8")
                components.html(html_content, height=800, scrolling=True)
            except Exception as e:
                st.warning(
                    f"Could not load report from S3: {e}. Ensure the Drift Monitor job has run."
                )

# =============================================================================
# Tab 3: Models
# =============================================================================
with tab3:
    st.subheader("Registered Models in MLflow")

    if not MlflowClient:
        st.error("MLflow library is not installed.")
    else:
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
        try:
            client = MlflowClient(tracking_uri=tracking_uri)
            models = client.search_registered_models()

            if not models:
                st.info("No registered models found in MLflow.")
            else:
                for rm in models:
                    with st.expander(f"📦 Model: {rm.name}", expanded=True):
                        st.markdown(f"**Description:** {rm.description or 'N/A'}")

                        # Display latest versions
                        if rm.latest_versions:
                            versions_data = []
                            for v in rm.latest_versions:
                                # Fetch run to get metrics
                                run = client.get_run(v.run_id)
                                metrics = run.data.metrics
                                accuracy = metrics.get("accuracy", "N/A")

                                versions_data.append(
                                    {
                                        "Version": v.version,
                                        "Aliases": ", ".join(v.aliases) if v.aliases else "-",
                                        "Status": v.status,
                                        "Accuracy": (
                                            f"{accuracy:.4f}"
                                            if isinstance(accuracy, float)
                                            else accuracy
                                        ),
                                        "Run ID": v.run_id,
                                    }
                                )

                            st.table(pd.DataFrame(versions_data))
                        else:
                            st.write("No versions found.")

        except Exception as e:
            st.error(f"Failed to connect to MLflow Tracking Server at {tracking_uri}: {e}")

# =============================================================================
# Tab 4: Simulation
# =============================================================================
with tab4:
    st.subheader("Generate & Send Simulated Traffic")
    st.markdown(
        "Inject mock tickets into the system to test load, graceful degradation, "
        "and data drift detection."
    )

    api_url = os.getenv("API_URL", "http://api:8000")

    c1, c2 = st.columns(2)
    with c1:
        num_tickets = st.number_input(
            "Number of Tickets to Generate", min_value=1, max_value=500, value=10
        )
    with c2:
        drift_mode = st.checkbox(
            "Enable Data Drift (Biased distribution towards German / Technical Support)"
        )

    if st.button("🚀 Generate & Send"):
        with st.spinner(f"Generating {num_tickets} tickets and sending to {api_url}..."):
            success_count = 0
            results = []

            for _ in range(num_tickets):
                if drift_mode:
                    payload = generate_drift_ticket()
                else:
                    payload = generate_ticket()

                try:
                    res = requests.post(f"{api_url}/tickets/", json=payload, timeout=5)
                    if res.status_code == 201:
                        success_count += 1
                        results.append(payload)
                except Exception:
                    pass

            st.success(f"Successfully sent {success_count} / {num_tickets} tickets!")

            # Since the API is asynchronous and shadow inference happens in the background,
            # we query the DB to get the predicted priorities for these newly generated tickets.
            if success_count > 0:
                ticket_ids = [t["ticket_id"] for t in results]
                id_tuple = tuple(ticket_ids)
                if len(id_tuple) == 1:
                    query = (
                        "SELECT ticket_id, subject, predicted_priority FROM tickets "
                        f"WHERE ticket_id = '{id_tuple[0]}'"
                    )
                else:
                    query = (
                        "SELECT ticket_id, subject, predicted_priority FROM tickets "
                        f"WHERE ticket_id IN {id_tuple}"
                    )

                df_results = pd.read_sql(query, engine)

                if not df_results.empty:
                    st.write("### Simulation Results Summary")
                    dist = (
                        df_results["predicted_priority"]
                        .fillna("unknown")
                        .value_counts()
                        .reset_index()
                    )
                    dist.columns = ["Priority", "Count"]
                    st.bar_chart(dist.set_index("Priority"))

                    st.write("### Generated Tickets Details")
                    st.dataframe(df_results, use_container_width=True)
