import streamlit as st
import pandas as pd
from database import connection_to_db
from fetch_jobs import fetch_and_store_jobs

STATUSES = ["Ej sökt", "Sökt", "Intervju", "Erbjudande", "Avslag"]
st.set_page_config(page_title="Jobbtracker", layout="wide")

def load_jobs():
    con = connection_to_db.connect_db()
    df = pd.read_sql("""
        SELECT j.api_job_id, j.title, c.company_name AS company, j.location,
               j.url, j.status, j.notes, j.applied_date
        FROM jobs j JOIN companies c ON j.company_id = c.company_id
    """, con)
    con.close()
    return df

def clean(value):
    # Gör om tomma rutor (nan) till "inget värde" som databasen förstår
    if pd.isna(value):
        return None
    return value


def save_job(row):
    con = connection_to_db.connect_db()
    cur = con.cursor()

    status = clean(row["status"]) or "Ej sökt"
    applied_date = clean(row["applied_date"])

    if applied_date is not None:
        applied_date = pd.to_datetime(applied_date).date()
    elif status != "Ej sökt":
        # Sökt men inget datum -> använd dagens datum
        applied_date = pd.Timestamp.today().date()

    cur.execute(
        "UPDATE jobs SET status=%s, notes=%s, applied_date=%s WHERE api_job_id=%s",
        (
            status,
            clean(row["notes"]),
            applied_date,
            row["api_job_id"],
        ),
    )
    con.commit()
    cur.close()
    con.close()


st.title("Mina ansökningar")

col1, col2 = st.columns([3, 1])
with col1:
    sokterm = st.text_input("Vilka jobb vill du hämta?", placeholder="t.ex. utvecklare, sjuksköterska, lärare")
with col2:
    st.write("")  # luft ovanför knappen
    st.write("")
    if st.button("↻ Hämta jobb från JobTech"):
        from fetch_jobs import fetch_and_store_jobs
        fetch_and_store_jobs(sokterm)
        st.success(f"Hämtade jobb för: {sokterm}")
        st.rerun()


df = load_jobs()
df["status"] = df["status"].fillna("Ej sökt")
df["applied_date"] = pd.to_datetime(df["applied_date"]).dt.date



# Statistik
sokta = df[df["status"] != "Ej sökt"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Sökta jobb", len(sokta))
c2.metric("Intervjuer", (df["status"] == "Intervju").sum())
c3.metric("Erbjudanden", (df["status"] == "Erbjudande").sum())
c4.metric("Avslag", (df["status"] == "Avslag").sum())

left, right = st.columns([2, 1])
with left:
    st.subheader("Sökta jobb per månad")
    per_man = sokta.dropna(subset=["applied_date"]).copy()
    if per_man.empty:
        st.info("Inga sökta jobb med datum än.")
    else:
        per_man["månad"] = pd.to_datetime(per_man["applied_date"]).dt.strftime("%Y-%m")
        st.bar_chart(per_man["månad"].value_counts().sort_index())
with right:
    st.subheader("Per status")
    st.bar_chart(df["status"].value_counts())



# Filter + tabell som går att redigera
sok = st.text_input("Sök jobb eller företag")
filt = st.selectbox("Status", ["Alla"] + STATUSES)
vy = df.copy()
if sok:
    vy = vy[vy["title"].str.contains(sok, case=False) | vy["company"].str.contains(sok, case=False)]
if filt != "Alla":
    vy = vy[vy["status"] == filt]

edited = st.data_editor(
    vy, hide_index=True, use_container_width=True,
    disabled=["api_job_id", "title", "company", "location", "url"],
    column_config={
        "api_job_id": None,
        "title": "Jobb", "company": "Företag", "location": "Ort",
        "url": st.column_config.LinkColumn("Annons"),
        "status": st.column_config.SelectboxColumn("Status", options=STATUSES),
        "notes": "Anteckningar",
        "applied_date": st.column_config.DateColumn("Sökt datum"),
    },
)

if st.button("Spara ändringar"):
    for _, row in edited.iterrows():
        save_job(row)
    st.success("Sparat!")
    st.rerun()