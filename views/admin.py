import streamlit as st
import mysql.connector
from database import get_connection


def show():
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title("🔐 Espace Administrateur")

    # 🧭 Menu horizontal avec icônes modernes
    menu = ["📊 Tableau de bord", "➕ Ajouter un étudiant", "🧾 Ajouter un résultat", "⚙️ Gérer les structures"]
    choice = st.selectbox("📁 Navigation des sections", menu)

    if choice == "📊 Tableau de bord":
        tableau_de_bord()
    elif choice == "➕ Ajouter un étudiant":
        ajouter_etudiant()
    elif choice == "🧾 Ajouter un résultat":
        ajouter_resultat()
    elif choice == "⚙️ Gérer les structures":
        gestion_structures()


# ------------------------------ #
# 📊 TABLEAU DE BORD

def tableau_de_bord():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM etudiants")
    total_etudiants = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM resultats")
    total_resultats = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM promotions")
    total_promotions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM facultes")
    total_facultes = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    st.markdown("""
        <div class="grid-dashboard">
            <div class="card-dashboard">
                <h3>👨‍🎓 Étudiants</h3><p>{}</p>
            </div>
            <div class="card-dashboard">
                <h3>📈 Résultats</h3><p>{}</p>
            </div>
            <div class="card-dashboard">
                <h3>🎓 Promotions</h3><p>{}</p>
            </div>
            <div class="card-dashboard">
                <h3>🏛 Facultés</h3><p>{}</p>
            </div>
        </div>
    """.format(total_etudiants, total_resultats, total_promotions, total_facultes), unsafe_allow_html=True)


# ------------------------------ #
# ➕ AJOUT D'ÉTUDIANT

def ajouter_etudiant():
    st.subheader("➕ Enregistrement d'un nouvel étudiant")

    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("👤 Nom complet")
    with col2:
        matricule = st.text_input("🆔 Matricule")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM promotions")
    promos = cursor.fetchall()
    cursor.close()
    conn.close()

    promo_options = {p[1]: p[0] for p in promos}
    promotion = st.selectbox("🎓 Promotion", list(promo_options.keys()))

    if st.button("💾 Enregistrer l'étudiant", use_container_width=True):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO etudiants (nom, matricule, promotion_id) VALUES (%s, %s, %s)",
                           (nom, matricule, promo_options[promotion]))
            conn.commit()
            st.success(f"✅ Étudiant {nom} ajouté avec succès.")
        except mysql.connector.Error as e:
            st.error(f"❌ Erreur : {e}")
        finally:
            cursor.close()
            conn.close()


# ------------------------------ #
# 🧾 AJOUT DE RÉSULTAT

def ajouter_resultat():
    st.subheader("🧾 Ajout des résultats d'un étudiant")

    # Initialisation de la session state
    if 'etu' not in st.session_state:
        st.session_state.etu = None

    matricule = st.text_input("Matricule de l’étudiant")

    if st.button("🔍 Rechercher"):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nom FROM etudiants WHERE matricule = %s", (matricule,))
        etu = cursor.fetchone()
        cursor.close()
        conn.close()

        if not etu:
            st.error("❌ Étudiant introuvable.")
        else:
            st.session_state.etu = etu
            st.success(f"✅ Étudiant : {etu['nom']} (ID: {etu['id']})")

    # ✅ Si l'étudiant a été trouvé et stocké
    if st.session_state.etu:
        etu = st.session_state.etu
        st.markdown(f"### Résultats pour : {etu['nom']}")

        with st.form(key="form_resultat"):
            # Ligne 1 : Moyenne / Mention
            col1, col2 = st.columns(2)
            with col1:
                moyenne = st.number_input("📝 Moyenne sur 20", min_value=0.0, max_value=20.0, step=0.1)
            with col2:
                mention = st.selectbox("📊 Mention", ["A", "B", "C", "D", "E"])

            # Ligne 2 : Crédits / Décision
            col3, col4 = st.columns(2)
            with col3:
                credits = st.number_input("🎯 Crédits validés", min_value=0, max_value=60, step=1)
            with col4:
                decision = st.selectbox("📌 Décision du jury", ["PASSE", "ECHEC", "AJOURNE"])

            # Ligne 3 : Session / Année
            col5, col6 = st.columns(2)
            with col5:
                session = st.selectbox("🕒 Session", ["Mi-session", "Semestre 1", "Semestre 2", "Deuxième session"])
            with col6:
                annee = st.text_input("📆 Année académique", placeholder="Ex: 2024-2025")

            # Bouton
            submit = st.form_submit_button("✅ Enregistrer le résultat", use_container_width=True)

            if submit:
                conn = get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO resultats (etudiant_id, moyenne, mention, credits_valides, decision_jury, session, annee_academique)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (etu["id"], moyenne, mention, credits, decision, session, annee))
                    conn.commit()
                    st.success("🎉 Résultat enregistré avec succès.")
                    st.session_state.etu = None  # Réinitialiser pour un autre étudiant
                except mysql.connector.Error as e:
                    st.error(f"❌ Erreur : {e}")
                finally:
                    cursor.close()
                    conn.close()




# ------------------------------ #
# ⚙️ GESTION DES STRUCTURES

def gestion_structures():
    st.subheader("⚙️ Gestion des promotions, départements et facultés")
    tab = st.tabs(["🏛 Facultés", "📚 Départements", "🎓 Promotions"])

    # Facultés
    with tab[0]:
        st.markdown("### ➕ Ajouter une nouvelle faculté")
        nom_fac = st.text_input("Nom de la faculté")
        if st.button("➕ Ajouter la faculté", use_container_width=True):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO facultes (nom) VALUES (%s)", (nom_fac,))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("✅ Faculté ajoutée.")

    # Départements
    with tab[1]:
        st.markdown("### ➕ Ajouter un département")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM facultes")
        facs = cursor.fetchall()
        cursor.close()
        conn.close()

        fac_options = {f[1]: f[0] for f in facs}
        nom_dep = st.text_input("Nom du département")
        fac_dep = st.selectbox("Faculté associée", list(fac_options.keys()))

        if st.button("➕ Ajouter le département", use_container_width=True):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO departements (nom, faculté_id) VALUES (%s, %s)", (nom_dep, fac_options[fac_dep]))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("✅ Département ajouté.")

    # Promotions
    with tab[2]:
        st.markdown("### ➕ Ajouter une promotion")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM departements")
        deps = cursor.fetchall()
        cursor.close()
        conn.close()

        dep_options = {d[1]: d[0] for d in deps}
        nom_prom = st.text_input("Nom de la promotion")
        dep_prom = st.selectbox("Département associé", list(dep_options.keys()))

        if st.button("➕ Ajouter la promotion", use_container_width=True):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO promotions (nom, departement_id) VALUES (%s, %s)", (nom_prom, dep_options[dep_prom]))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("✅ Promotion ajoutée.")
