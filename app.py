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

# Fonction pour charger les données avec toutes les colonnes requises
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # S'assurer que toutes les colonnes existent
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

# --- Barre latérale (Sidebar) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/constructor.png", width=80)
    st.title("Panneau de Contrôle")
    
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
                st.error("Identifiants incorrects.")
    else:
        st.success("👤 Administrateur connecté")
        if st.button("Se déconnecter"):
            st.session_state.authenticated = False
            st.rerun()
            
        st.markdown("---")
        st.subheader("➕ Ajouter / Mettre à jour une Poutre")
        
        with st.form("add_form", clear_on_submit=True):
            poutre_id = st.text_input("ID de la Poutre (ex: DP1-01)")
            p_type = st.selectbox("Type de Poutre", ["DP1", "DP2", "DP3", "DP4", "DP5"])
            
            # المراحل الشاملة
            etape = st.selectbox("Étape Actuelle", [
                "Coffrage (كوفراج)", 
                "Ferraillage (تسليح)", 
                "Coulage (صب خرسانة)", 
                "Décoffrage (فك الكوفراج)"
            ])
            
            # نوعية العمال الشاملة
            specialite = st.selectbox("Spécialité des Ouvriers", [
                "Coffreurs (نجارين)", 
                "Ferrailleurs (حدادين)", 
                "Equipe Béton (عمال خرسانة)", 
                "Équipe Mixte / Générale (فريق مختلط)"
            ])
            
            effectif = st.number_input("Nombre d'ouvriers", min_value=1, max_value=100, value=5)
            
            # حالة انتهاء الأشغال
            statut = st.selectbox("Statut des Travaux", [
                "En Cours (قيد الانجاز)", 
                "Terminé / Réceptionné (تم الانتهاء / استلام)", 
                "En Attente / Bloqué (معلق / في الانتظار)"
            ])
            
            date_saisie = st.date_input("Date de l'opération")
            
            submitted = st.form_submit_button("Enregistrer les modifications")
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
                    st.success(f"Poutre {poutre_id} mise à jour avec succès !")
                    st.rerun()
                else:
                    st.warning("Veuillez entrer l'ID de la poutre.")

# --- Interface Principale ---
st.title("🏗️ Tableau de Bord - Projet Pont Gholoul")
st.markdown("Suivi technique approfondi : Étapes, Spécialités des ouvriers et Statut des travaux.")
st.markdown("---")

if not df.empty:
    # 1. Indicateurs clés (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    
    total_poutres = df["ID_Poutre"].nunique()
    total_workers = int(df["Effectif"].sum())
    completed_works = len(df[df["Statut"].str.contains("Terminé", na=False)])
    ongoing_works = len(df[df["Statut"].str.contains("En Cours", na=False)])
    
    col1.metric(label="📊 Total Poutres Suivies", value=total_poutres)
    col2.metric(label="👷 Total Main-d'œuvre", value=total_workers)
    col3.metric(label="✅ Travaux Terminés", value=completed_works)
    col4.metric(label="🔄 Travaux En Cours", value=ongoing_works)
    
    st.markdown("---")
    
    # 2. Graphiques Modernes et Complets (Plotly)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 Distribution par Spécialité d'Ouvriers")
        fig_spec = px.pie(
            df, 
            names='Specialite_Ouvriers', 
            values='Effectif',
            hole=0.4, 
            color_discrete_sequence=px.colors.sequential.Sunset
        )
        fig_spec.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_spec, use_container_width=True)
        
    with col_chart2:
        st.subheader("📊 Avancement selon le Statut des Travaux")
        fig_status = px.bar(
            df, 
            x='Type', 
            y='Effectif', 
            color='Statut',
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_status.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)

    st.markdown("---")
    
    # 3. Tableau détaillé complet
    st.subheader("📋 Registre Technique Détaillé")
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
  
