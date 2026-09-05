import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text  # مكتبة ضرورية لتغليف جمل SQL في SQLAlchemy الحديثة

# Configuration de la page
st.set_page_config(
    page_title="Gestion du Pont - Gholoul",
    page_icon="🏗️",
    layout="wide"
)

# --- إعداد الاتصال بقاعدة بيانات SQL السحابية ---
try:
    conn = st.connection("postgresql", type="sql")
except Exception as e:
    st.error(f"Erreur de configuration de la base de données: {e}")

# إنشاء الجدول تلقائياً إذا لم يكن موجوداً
def init_db():
    with conn.session as s:
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS poutres (
                id SERIAL PRIMARY KEY,
                id_poutre TEXT,
                type TEXT,
                etape TEXT,
                specialite_ouvriers TEXT,
                effectif INTEGER,
                statut TEXT,
                date TEXT
            );
        '''))
        s.commit()

init_db()

# --- جلب البيانات من SQL ---
def load_data():
    try:
        df = conn.query("SELECT * FROM poutres;", ttl=0)
        if not df.empty and "id" in df.columns:
            df = df.drop(columns=["id"])
        else:
            df = pd.DataFrame(columns=["id_poutre", "type", "etape", "specialite_ouvriers", "effectif", "statut", "date"])
        
        df = df.rename(columns={
            "id_poutre": "ID_Poutre",
            "type": "Type",
            "etape": "Etape",
            "specialite_ouvriers": "Specialite_Ouvriers",
            "effectif": "Effectif",
            "statut": "Statut",
            "date": "Date"
        })
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données SQL: {e}")
        return pd.DataFrame(columns=["ID_Poutre", "Type", "Etape", "Specialite_Ouvriers", "Effectif", "Statut", "Date"])

# --- حفظ صف جديد في SQL ---
def save_data_row(poutre_id, p_type, etape, specialite, effectif, statut, date_saisie):
    try:
        with conn.session as s:
            s.execute(
                text('''
                INSERT INTO poutres (id_poutre, type, etape, specialite_ouvriers, effectif, statut, date)
                VALUES (:poutre_id, :p_type, :etape, :specialite, :effectif, :statut, :date_saisie)
                '''),
                {
                    "poutre_id": poutre_id,
                    "p_type": p_type,
                    "etape": etape,
                    "specialite": specialite,
                    "effectif": int(effectif),
                    "statut": statut,
                    "date_saisie": str(date_saisie)
                }
            )
            s.commit()
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement: {e}")
        return False

# --- مسح الجدول بالكامل ---
def clear_all_data():
    try:
        with conn.session as s:
            s.execute(text("DELETE FROM poutres;"))
            s.commit()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la réinitialisation: {e}")
        return False
