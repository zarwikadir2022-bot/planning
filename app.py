import streamlit as st
import pandas as pd
import os
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="Suivi Pont - Gholoul", page_icon="🏗️", layout="wide")

DB_FILE = "gholoul_bridge_data.csv"

# وظيفة لتحميل البيانات
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        df = pd.DataFrame(columns=[
            "ID Poutre", "Type", "Étape", "Avancement", 
            "Nombre d'ouvriers", "Type d'ouvriers", "Date"
        ])
        df.to_csv(DB_FILE, index=False)
        return df

df = load_data()

st.title("🏗️ Tableau de bord - Coulage des Dalles préfabriqués (Entreprise Gholoul)")
st.markdown("Suivi en temps réel des types de dalles (DP1 à DP5), des étapes et de la main-d'œuvre.")

# --- نظام تسجيل الدخول (Sidebar) ---
st.sidebar.header("🔐 Connexion Administrateur")

# تهيئة حالة الجلسة (Session State) لتسجيل الدخول
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    with st.sidebar.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        login_btn = st.form_submit_button("Se connecter")
        
        if login_btn:
            if username == "gholoul_admin" and password == "12345":
                st.session_state["authenticated"] = True
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")
    st.sidebar.info("💡 Mode lecture seule. Connectez-vous pour modifier les données.")
else:
    st.sidebar.success("✅ Connecté en tant qu'admin")
    if st.sidebar.button("Déconnexion"):
        st.session_state["authenticated"] = False
        st.rerun()

st.divider()

# --- واجهة العرض والإحصائيات (تظهر للجميع) ---
st.header("📊 Tableau de bord et Statistiques")

if not df.empty:
    # مؤشرات سريعة (KPIs)
    total_dallas = len(df)
    total_workers = df["Nombre d'ouvriers"].sum() if "Nombre d'ouvriers" in df.columns else 0
    
    m1, m2 = st.columns(2)
    m1.metric("Total des enregistrements", total_dallas)
    m2.metric("Total des ouvriers sur site", total_workers)
    
    st.divider()
    
    # تصفية البيانات حسب النوع
    filter_type = st.selectbox("Filtrer par type de poutre :", ["Tous", "DP1", "DP2", "DP3", "DP4", "DP5"])
    if filter_type != "Tous":
        filtered_df = df[df["Type"] == filter_type]
    else:
        filtered_df = df
        
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("Aucune donnée enregistrée pour le moment.")

# --- قسم إدخال وتعديل البيانات (يظهر فقط إذا تم تسجيل الدخول) ---
if st.session_state["authenticated"]:
    st.divider()
    st.header("➕ Saisie et Modification des Données (Réservé aux superviseurs)")
    
    with st.form("dalla_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dalla_id = st.text_input("ID de la poutre (ex: DP1-01)")
            dalla_type = st.selectbox("Type de poutre", ["DP1", "DP2", "DP3", "DP4", "DP5"])
            stage = st.selectbox("Étape actuelle", ["Coffrage", "Frappe / Armature", "Coulage Béton", "Démoulage / Cure", "Terminé"])
            
        with col2:
            progress = st.slider("Pourcentage d'avancement (%)", 0, 100, 0)
            worker_count = st.number_input("Nombre d'ouvriers", min_value=1, value=5)
            
        with col3:
            worker_type = st.selectbox("Spécialité des ouvriers", ["Ferrailleurs", "Coffreurs", "Ouvriers béton", "Ingénieurs / Chefs", "Mixte"])
            date_logged = st.date_input("Date", datetime.now())
            
        submit_btn = st.form_submit_button("Enregistrer")
        
        if submit_btn:
            if dalla_id:
                new_data = pd.DataFrame({
                    "ID Poutre": [dalla_id],
                    "Type": [dalla_type],
                    "Étape": [stage],
                    "Avancement": [f"{progress}%"],
                    "Nombre d'ouvriers": [worker_count],
                    "Type d'ouvriers": [worker_type],
                    "Date": [str(date_logged)]
                })
                
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success(f"Poutre {dalla_id} enregistrée avec succès !")
                st.rerun()
            else:
                st.error("Veuillez entrer l'ID de la poutre.")
                
    # زر لحذف البيانات عند الحاجة
    if st.button("Supprimer toutes les données"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.rerun()
else:
    st.warning("🔒 Le formulaire de saisie est masqué. Veuillez vous connecter via la barre latérale pour ajouter ou modifier des données.")
