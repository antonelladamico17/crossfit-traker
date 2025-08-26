import streamlit as st
import sqlite3
from datetime import date

# ---- DATABASE ----
conn = sqlite3.connect("crossfit.db", check_same_thread=False)
c = conn.cursor()

# Tabelle
c.execute("""CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    notes TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER,
    name TEXT,
    weight REAL,
    reps INTEGER,
    time TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS max_lifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    weight REAL,
    date TEXT
)""")

conn.commit()

# ---- FUNZIONI ----
def add_workout(date, notes):
    c.execute("INSERT INTO workouts (date, notes) VALUES (?, ?)", (date, notes))
    conn.commit()
    return c.lastrowid

def add_exercise(workout_id, name, weight, reps, time):
    c.execute("INSERT INTO exercises (workout_id, name, weight, reps, time) VALUES (?, ?, ?, ?, ?)",
              (workout_id, name, weight, reps, time))
    conn.commit()

def add_max_lift(name, weight, date):
    c.execute("INSERT INTO max_lifts (name, weight, date) VALUES (?, ?, ?)", (name, weight, date))
    conn.commit()

# ---- INTERFACCIA ----
st.title("🏋️ CrossFit Tracker")

menu = st.sidebar.radio("Menu", ["Home", "Aggiungi Workout", "Storico", "Massimali"])

if menu == "Home":
    st.header("Benvenuto nel tuo diario CrossFit 💪")
    st.write("Usa il menu a sinistra per aggiungere o consultare i tuoi allenamenti.")

elif menu == "Aggiungi Workout":
    st.header("➕ Nuovo Workout")
    notes = st.text_input("Note generali")
    if st.button("Crea Workout"):
        wid = add_workout(date.today().isoformat(), notes)
        st.success(f"Workout {wid} creato!")

    st.subheader("Aggiungi esercizi")
    with st.form("ex_form"):
        workout_id = st.number_input("ID workout", min_value=1, step=1)
        name = st.text_input("Nome esercizio")
        weight = st.number_input("Peso (kg)", min_value=0.0, step=1.0)
        reps = st.number_input("Ripetizioni", min_value=0, step=1)
        time = st.text_input("Tempo/Score")
        submitted = st.form_submit_button("Aggiungi esercizio")
        if submitted:
            add_exercise(workout_id, name, weight, reps, time)
            st.success("Esercizio aggiunto!")

elif menu == "Storico":
    st.header("📅 Storico Workout")
    workouts = c.execute("SELECT * FROM workouts ORDER BY date DESC").fetchall()
    for w in workouts:
        st.subheader(f"Workout {w[0]} - {w[1]}")
        st.write(w[2])
        exs = c.execute("SELECT name, weight, reps, time FROM exercises WHERE workout_id=?", (w[0],)).fetchall()
        st.table(exs)

elif menu == "Massimali":
    st.header("🏆 Massimali")
    with st.form("max_form"):
        name = st.text_input("Esercizio")
        weight = st.number_input("Peso max (kg)", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Salva massimale")
        if submitted:
            add_max_lift(name, weight, date.today().isoformat())
            st.success("Massimale salvato!")

    maxes = c.execute("SELECT name, MAX(weight) as best FROM max_lifts GROUP BY name").fetchall()
    st.table(maxes)
