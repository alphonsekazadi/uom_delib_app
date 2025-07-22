# main.py

import streamlit as st
from views import accueil, recherche, admin, gestion_facultes
from auth import login, create_user_etudiant, is_authenticated, logout
from database import get_connection

st.set_page_config(page_title="UOM Résultats", layout="wide")

# 💄 Cacher Streamlit standard UI
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 💅 Appliquer le CSS
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 👮 Authentification obligatoire
if not is_authenticated():
    # FORMULAIRE DE CONNEXION
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<div class='login-icon'>🔐</div>", unsafe_allow_html=True)
    st.markdown("<h2>Connexion à l'espace UOM</h2>", unsafe_allow_html=True)

    choix = st.radio("Choisissez une option", ["Se connecter", "Créer un compte"], horizontal=True)

    if choix == "Se connecter":
        email = st.text_input("Adresse e-mail")
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

    st.markdown("</div></div>", unsafe_allow_html=True)  # Fin du formulaire centré
    st.stop()


# ✅ Utilisateur connecté
user = st.session_state.user
role = user["role"]

# 🔁 Gérer déconnexion via URL ?logout=true
if st.query_params.get("logout") == "true":
    logout()
    st.query_params.clear()
    st.rerun()

# 🔁 Lire la page active depuis l’URL (par défaut accueil)
page = st.query_params.get("page", "accueil")

# 🧭 Définir le menu
menu_items = {
    "accueil": "Accueil",
    "recherche": "Recherche"
}
if role == "admin":
    menu_items["admin"] = "Admin"
    menu_items["facultes"] = "Facultés"

# 🌐 Navbar HTML
nav_html = '<div class="navbar"><div class="nav-left">'
for key, label in menu_items.items():
    active = "active" if page == key else ""
    nav_html += f'<a href="?page={key}" class="nav-link {active}">{label}</a>'
nav_html += '</div><div class="nav-right">'
nav_html += f'<span class="user-info">👤 {user["nom"]} {"("+user["matricule"]+")" if role == "etudiant" else ""}</span>'
nav_html += f'<a href="?logout=true" class="logout-link">Déconnexion</a>'
nav_html += '</div></div>'
st.markdown(nav_html, unsafe_allow_html=True)

# 🧾 Afficher la page correspondante
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
