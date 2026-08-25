import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuration de la page (Mode Wide + Design Pro)
st.set_page_config(
    page_title="Gestion du Pont - Gholoul",
    page_icon="🏗️",
    layout="wide"
)

# Application de styles CSS personnalisés pour un look professionnel (Construction & Engineering theme)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #0056b3;
    }
    .stSubheader {
        color: #2c3e50;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# Fichier de données local
DATA_FILE = "gholoul_data.csv"

# Fonction pour charger les données
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        expected_columns = ["ID_Poutre", "Type", "Etape", "Specialite_Ouvriers", "Effectif", "Statut", "Date"]
        for col in expected_columns:
            if col not in df.columns:
                df[col] = "N/A"
        return df
    else:
        df_default = pd.DataFrame(columns=["ID_Poutre", "Type", "Etape", "Specialite_Ouvriers", "Effectif", "Statut", "Date"])
        df_default.to_csv(DATA_FILE, index=False)
        return df_default

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# --- Barre latérale (Sidebar) - Espace Admin ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/constructor.png", width=70)
    st.title("Panneau de Contrôle")
    st.markdown("---")
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.subheader("🔑 Connexion Admin")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter", use_container_width=True):
            if username == "gholoul_admin" and password == "12345":
                st.session_state.authenticated = True
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
    else:
        st.success("👤 Administrateur Connecté")
        if st.button("Se déconnecter", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
            
        st.markdown("---")
        st.subheader("➕ Saisie & Mise à Jour")
        
        with st.form("add_form", clear_on_submit=True):
            poutre_id = st.text_input("ID de la Poutre (ex: DP1-01)")
            p_type = st.selectbox("Type de Poutre", ["DP1", "DP2", "DP3", "DP4", "DP5"])
            
            etape = st.selectbox("Étape Actuelle", [
                "Coffrage", 
                "Ferraillage", 
                "Coulage", 
                "Décoffrage"
            ])
            
            specialite = st.selectbox("Spécialité des Ouvriers", [
                "Coffreurs", 
                "Ferrailleurs", 
                "Équipe Béton", 
                "Équipe Mixte"
            ])
            
            effectif = st.number_input("Nombre d'ouvriers", min_value=1, max_value=100, value=5)
            
            statut = st.selectbox("Statut des Travaux", [
                "En Cours", 
                "Terminé / Réceptionné", 
                "En Attente / Bloqué"
            ])
            
            date_saisie = st.date_input("Date de l'opération")
            
            submitted = st.form_submit_button("Enregistrer", use_container_width=True)
            if submitted:
                if poutre_id:
                    new_row = pd.DataFrame({
                        "ID_Poutre": [poutre_id],
                        "Type": [p_type],
                        "Etape": [etape],
                        "Specialite_Ouvriers": [specialite],
                        "Effectif": [effectif],
                        "Statut": [statut],
                        "Date": [str(date_saisie)]
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success(f"Poutre {poutre_id} enregistrée !")
                    st.rerun()
                else:
                    st.warning("Veuillez entrer l'ID de la poutre.")

# --- Interface Principale ---
st.title("🏗️ Tableau de Bord - Projet Pont Gholoul")
st.markdown("Suivi centralisé des opérations, de la main-d'œuvre et de l'avancement par type de poutre.")
st.markdown("---")

if not df.empty:
    # 1. Indicateurs Clés Globaux (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    
    total_poutres = df["ID_Poutre"].nunique()
    total_workers = int(df["Effectif"].sum())
    completed_works = len(df[df["Statut"].str.contains("Terminé", na=False)])
    ongoing_works = len(df[df["Statut"].str.contains("En Cours", na=False)])
    
    col1.metric(label="📊 Total Poutres", value=total_poutres)
    col2.metric(label="👷 Total Ouvriers", value=total_workers)
    col3.metric(label="✅ Terminés / Réceptionnés", value=completed_works)
    col4.metric(label="🔄 En Cours", value=ongoing_works)
    
    st.markdown("---")
    
    # 2. Statistiques Globales et Graphiques Avancés
    st.subheader("📈 Analyses Globales du Chantier")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig_spec = px.pie(
            df, 
            names='Specialite_Ouvriers', 
            values='Effectif',
            title="Répartition de la Main-d'œuvre par Spécialité",
            hole=0.4, 
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig_spec.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_spec, use_container_width=True)
        
    with col_chart2:
        fig_status = px.bar(
            df, 
            x='Type', 
            y='Effectif', 
            color='Statut',
            title="Volume de Main-d'œuvre par Type de Poutre et Statut",
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_status.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)

    st.markdown("---")

    # 3. Sections Spécifiques par Type de Poutre (DP1 à DP5)
    st.subheader("📑 Sections Détaillées par Type de Poutre (DP1 - DP5)")
    
    poutre_types = ["DP1", "DP2", "DP3", "DP4", "DP5"]
    tabs = st.tabs([f"Type {p}" for p in poutre_types])
    
    for i, p_type in enumerate(poutre_types):
        with tabs[i]:
            df_filtered = df[df["Type"] == p_type]
            if not df_filtered.empty:
                col_t1, col_t2 = st.columns(2)
                col_t1.metric(f"Éléments {p_type} Enregistrés", len(df_filtered))
                col_t2.metric(f"Ouvriers sur {p_type}", int(df_filtered["Effectif"].sum()))
                
                st.dataframe(df_filtered, use_container_width=True)
                
                # Graphique individuel pour chaque type
                fig_sub = px.bar(
                    df_filtered, 
                    x='ID_Poutre', 
                    y='Effectif', 
                    color='Etape',
                    title=f"Détails des étapes pour le {p_type}",
                    color_discrete_sequence=px.colors.sequential.Teal
                )
                st.plotly_chart(fig_sub, use_container_width=True)
            else:
                st.info(f"Aucune donnée enregistrée pour le type {p_type} pour le moment.")

    st.markdown("---")
    
    # 4. Registre Technique Global
    st.subheader("📋 Registre Technique Général")
    st.dataframe(df, use_container_width=True)
    
    # Bouton de réinitialisation
    if st.session_state.authenticated:
        if st.button("🗑️ Réinitialiser toutes les données", type="secondary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("Données supprimées avec succès.")
            st.rerun()

else:
    st.info("📌 Aucune donnée enregistrée. Connectez-vous via la barre latérale pour commencer l'enregistrement.")
