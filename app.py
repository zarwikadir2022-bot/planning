import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuration de la page
st.set_page_config(
    page_title="Gestion du Pont - Gholoul",
    page_icon="🏗️",
    layout="wide"
)

# Fichier de données local
DATA_FILE = "gholoul_data.csv"

# Fonction pour charger les données
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df_default = pd.DataFrame(columns=["ID_Poutre", "Type", "Etape", "Effectif", "Date"])
        df_default.to_csv(DATA_FILE, index=False)
        return df_default

# Fonction pour sauvegarder les données
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# --- Barre latérale (Sidebar) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/constructor.png", width=80)
    st.title("Panneau de Contrôle")
    
    # État de l'authentification
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.subheader("🔑 Connexion Admin")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            if username == "gholoul_admin" and password == "12345":
                st.session_state.authenticated = True
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")
    else:
        st.success("👤 Connecté en tant que: Administrateur")
        if st.button("Se déconnecter"):
            st.session_state.authenticated = False
            st.rerun()
            
        st.markdown("---")
        st.subheader("➕ Ajouter une Poutre")
        
        with st.form("add_form", clear_on_submit=True):
            poutre_id = st.text_input("ID de la Poutre (ex: DP1-01)")
            p_type = st.selectbox("Type de Poutre", ["DP1", "DP2", "DP3", "DP4", "DP5"])
            etape = st.selectbox("Étape", ["Coffrage", "Ferraillage", "Coulage", "Décoffrage"])
            effectif = st.number_input("Nombre d'ouvriers", min_value=1, max_value=100, value=5)
            date_saisie = st.date_input("Date")
            
            submitted = st.form_submit_button("Enregistrer")
            if submitted:
                if poutre_id:
                    new_row = pd.DataFrame({
                        "ID_Poutre": [poutre_id],
                        "Type": [p_type],
                        "Etape": [etape],
                        "Effectif": [effectif],
                        "Date": [str(date_saisie)]
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success(f"Poutre {poutre_id} ajoutée avec succès !")
                    st.rerun()
                else:
                    st.warning("Veuillez entrer l'ID de la poutre.")

# --- Interface Principale ---
st.title("🏗️ Tableau de Bord - Projet Pont Gholoul")
st.markdown("Suivi en temps réel de l'avancement des étapes et de la main-d'œuvre sur le site.")
st.markdown("---")

if not df.empty:
    # 1. Indicateurs clés (KPIs)
    col1, col2, col3 = st.columns(3)
    
    total_poutres = len(df)
    total_workers = int(df["Effectif"].sum())
    latest_stage = df.iloc[-1]["Etape"] if not df.empty else "N/A"
    
    col1.metric(label="📊 Total des Poutres / Enregistrements", value=total_poutres)
    col2.metric(label="👷 Total des Ouvriers", value=total_workers)
    col3.metric(label="🔄 Dernière Étape Enregistrée", value=latest_stage)
    
    st.markdown("---")
    
    # 2. Graphiques Modernes (Plotly)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 Distribution par Étape")
        fig_pie = px.pie(
            df, 
            names='Etape', 
            hole=0.4, 
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.subheader("👥 Ouvriers par Type de Poutre")
        fig_bar = px.bar(
            df, 
            x='Type', 
            y='Effectif', 
            color='Etape',
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    
    # 3. Tableau détaillé
    st.subheader("📋 Registre Détaillé des Opérations")
    st.dataframe(df, use_container_width=True)
    
    # Bouton de réinitialisation
    if st.session_state.authenticated:
        if st.button("🗑️ Réinitialiser toutes les données", type="secondary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("Données supprimées avec succès.")
            st.rerun()

else:
    st.info("📌 Aucune donnée enregistrée pour le moment. Utilisez la barre latérale pour vous connecter et ajouter des éléments.")
