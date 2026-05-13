import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Page Config
st.set_page_config(page_title="Ticket Triage Stream", page_icon="🎫", layout="wide")

# Application Title
st.title("🎫 Ticket Triage Stream Dashboard")
st.markdown("Real-time view of incoming support tickets.")


# Setup DB Connection
@st.cache_resource
def get_db_engine():
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://tickets_user:tickets_pass@localhost:5432/tickets_db"
    )
    # Streamlit uses sync pandas read_sql, so replace asyncpg with default psycopg2
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")

    engine = create_engine(db_url)
    return engine


def fetch_latest_tickets(engine, limit=50):
    query = f"SELECT * FROM tickets ORDER BY timestamp DESC LIMIT {limit}"
    df = pd.read_sql(query, engine)
    return df


# Main logic
try:
    engine = get_db_engine()

    # Refresh mechanism
    col1, col2 = st.columns([9, 1])
    with col2:
        st.button("🔄 Refresh Data")

    df = fetch_latest_tickets(engine)

    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No tickets found in the database. Start the simulator to generate traffic.")

except Exception as e:
    st.error(f"Failed to connect to the database or fetch data: {str(e)}")
