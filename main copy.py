# main.py

import streamlit as st
from views import accueil, recherche, admin, gestion_facultes
from auth import login, create_user_etudiant, is_authenticated, logout
from database import get_connection

st.set_page_config(page_title="UOM Résultats", layout="wide")

# 🔒 Masquer menu Streamlit et padding
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 🧼 Charger CSS externe
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 🔁 Initialiser la page dans session_state
if "page" not in st.session_state:
    st.session_state.page = "accueil"

def go_to_page(page):
    st.session_state.page = page
    st.rerun()

# 🔐 Auth obligatoire
if not is_authenticated():
    st.title("🔐 Connexion à l'espace UOM")

    choix = st.radio("Choisissez une option", ["Se connecter", "Créer un compte"], horizontal=True)

    if choix == "Se connecter":
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Connexion"):
            if login(email, password):
                st.success("Connexion réussie.")
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")
    else:
        nom = st.text_input("Nom complet")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        matricule = st.text_input("Matricule")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM promotions")
        promotions = cursor.fetchall()
        cursor.close()
        conn.close()

        promo_map = {p[1]: p[0] for p in promotions}
        promo_nom = st.selectbox("Promotion", list(promo_map.keys()))
        promo_id = promo_map[promo_nom]

        if st.button("Créer mon compte"):
            if create_user_etudiant(nom, email, password, matricule, promo_id):
                st.success("Compte créé. Veuillez vous connecter.")
            else:
                st.error("Erreur lors de la création.")
    st.stop()

# ✅ Utilisateur connecté
user = st.session_state.user
role = user["role"]

# Menu selon rôle
menu_items = {
    "accueil": "Accueil",
    "recherche": "Recherche"
}
if role == "admin":
    menu_items["admin"] = "Admin"
    menu_items["facultes"] = "Facultés"

# 🔍 Génération NAVBAR HTML avec onclick
nav_html = '<div class="navbar"><div class="nav-left">'
for key, label in menu_items.items():
    active = 'active' if st.session_state.page == key else ''
    nav_html += f'<a href="javascript:void(0);" class="nav-link {active}" onclick="document.cookie = \'page={key}\'; window.location.reload();">{label}</a>'
nav_html += '</div><div class="nav-right">'
nav_html += f'<span class="user-info">👤 {user["nom"]} {"("+user["matricule"]+")" if role == "etudiant" else ""}</span>'
nav_html += f'<a href="javascript:void(0);" class="logout-link" onclick="document.cookie=\'logout=true\'; window.location.reload();">Déconnexion</a>'
nav_html += '</div></div>'

# Injecter HTML navbar
st.markdown(nav_html, unsafe_allow_html=True)

# Gestion du cookie de navigation
import streamlit.components.v1 as components
components.html("""
    <script>
        const cookies = document.cookie.split("; ");
        let logout = cookies.find(c => c.startsWith("logout=true"));
        let page = cookies.find(c => c.startsWith("page="));
        if (logout) {
            fetch("/?logout=true").then(() => document.cookie = 'logout=; Max-Age=0; path=/');
        }
        if (page) {
            let val = page.split("=")[1];
            window.parent.postMessage({type: "streamlit:setComponentValue", value: val}, "*");
            document.cookie = 'page=; Max-Age=0; path=/';
        }
    </script>
""", height=0)

# Déconnexion ?
if st.query_params.get("logout") == "true":
    logout()
    st.rerun()

# Affichage de la page active
page = st.session_state.page
if page == "accueil":
    accueil.show()
elif page == "recherche":
    recherche.show()
elif page == "admin" and role == "admin":
    admin.show()
elif page == "facultes" and role == "admin":
    gestion_facultes.show()
else:
    st.warning("Page non autorisée.")
