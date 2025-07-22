import streamlit as st
from database import get_connection
from fpdf import FPDF
import uuid
import os
import unicodedata

def show():
    # CSS
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title("🔍 Recherche des résultats de délibération")

    st.markdown("""
        <p class='intro-text'>
            Veuillez saisir le <strong>nom</strong> ou le <strong>matricule</strong> de l'étudiant pour consulter ses résultats :
        </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        nom_input = st.text_input("👤 Nom complet")
    with col2:
        matricule_input = st.text_input("🆔 Matricule")

    # 👉 Bouton en dessous des deux champs (et non dans col2)
    if st.button("🔎 Rechercher", use_container_width=True):
        if not nom_input.strip() and not matricule_input.strip():
            st.warning("❗ Veuillez fournir au moins un champ.")
            return

        # Vérifie que le nom est complet
        if nom_input:
            mots = nom_input.strip().split()
            if len(mots) < 2:
                st.warning("❗ Veuillez saisir le **nom complet** de l’étudiant (au moins prénom + nom).")
                return

        results = rechercher_etudiant(nom_input, matricule_input)

        if not results:
            st.error("❌ Aucun résultat trouvé.")
        else:
            cols = st.columns(2)  # Affichage à 2 bulletins côte à côte
            for i, r in enumerate(results):
                with cols[i % 2]:
                    afficher_bulletin_tableau(r)
                if (i + 1) % 2 == 0:
                    cols = st.columns(2)
 


def rechercher_etudiant(nom, matricule):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            e.matricule,
            e.nom,
            f.nom AS faculté,
            d.nom AS département,
            p.nom AS promotion,
            r.moyenne,
            r.mention,
            r.credits_valides,
            r.decision_jury,
            r.session,
            r.annee_academique
        FROM resultats r
        JOIN etudiants e ON r.etudiant_id = e.id
        JOIN promotions p ON e.promotion_id = p.id
        JOIN departements d ON p.departement_id = d.id
        JOIN facultes f ON d.faculté_id = f.id
        WHERE 1=1
    """

    params = []
    if nom:
        query += " AND e.nom LIKE %s"
        params.append(f"%{nom}%")
    if matricule:
        query += " AND e.matricule LIKE %s"
        params.append(f"%{matricule}%")

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def afficher_bulletin_tableau(data):
    html_bulletin = f"""
        <div class="bulletin">
            <h3>📘 Bulletin des côtes</h3>
            <table class="info-table">
                <tr><th>👤 Nom</th><td>{data['nom']}</td></tr>
                <tr><th>🆔 Matricule</th><td>{data['matricule']}</td></tr>
                <tr><th>🎓 Promotion</th><td>{data['promotion']}</td></tr>
                <tr><th>🏛 Faculté</th><td>{data['faculté']}</td></tr>
                <tr><th>📚 Département</th><td>{data['département']}</td></tr>
                <tr><th>📆 Année</th><td>{data['annee_academique']}</td></tr>
                <tr><th>🕒 Session</th><td>{data['session']}</td></tr>
                <tr><th><h4>📊 Résultats</h4></th></tr>
                <tr><th>Moyenne</th><td>{data['moyenne']} / 20</td></tr>
                <tr><th>Mention</th><td>{data['mention']}</td></tr>
                <tr><th>Crédits validés</th><td>{data['credits_valides']}</td></tr>
                <tr><th>Décision du jury</th><td>{data['decision_jury']}</td></tr>
            </table>
        </div>
    """
    
    st.markdown(html_bulletin, unsafe_allow_html=True)

    pdf_path = generer_bulletin_pdf(data)

    with open(pdf_path, "rb") as f:
        st.download_button(
        label="📥 Télécharger le bulletin en PDF",
        data=f,
        file_name=f"Bulletin_{data['matricule']}.pdf",
        mime="application/pdf",
        key=f"download_{data['matricule']}_{uuid.uuid4()}"
    )


# 🔧 Fonction de nettoyage
def nettoyer_texte(txt):
    if not isinstance(txt, str):
        txt = str(txt)
    return ''.join(c for c in unicodedata.normalize('NFKD', txt) if ord(c) < 256)

# ✅ Fonction de génération du PDF
def generer_bulletin_pdf(data, logo_path="assets/logo_uom.png"):
    pdf = FPDF()
    pdf.add_page()

    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, nettoyer_texte("Université Officielle de Mbujimayi"), ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, nettoyer_texte("Bulletin des côtes - Année académique 2024-2025"), ln=True, align='C')

    pdf.ln(10)
    pdf.set_font("Arial", '', 11)

    infos = [
        ("Nom", data['nom']),
        ("Matricule", data['matricule']),
        ("Promotion", data['promotion']),
        ("Faculté", data['faculté']),
        ("Département", data['département']),
        ("Année académique", data['annee_academique']),
        ("Session", data['session'])
    ]
    for label, val in infos:
        pdf.cell(50, 8, nettoyer_texte(f"{label} :"), border=0)
        pdf.cell(0, 8, nettoyer_texte(val), ln=True, border=0)

    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, nettoyer_texte("Résultats obtenus"), ln=True)

    pdf.set_font("Arial", '', 11)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(50, 8, nettoyer_texte("Moyenne"), 1, 0, 'C', True)
    pdf.cell(40, 8, nettoyer_texte("Mention"), 1, 0, 'C', True)
    pdf.cell(50, 8, nettoyer_texte("Crédits validés"), 1, 0, 'C', True)
    pdf.cell(50, 8, nettoyer_texte("Décision du jury"), 1, 1, 'C', True)

    pdf.cell(50, 8, nettoyer_texte(f"{data['moyenne']} / 20"), 1)
    pdf.cell(40, 8, nettoyer_texte(data['mention']), 1)
    pdf.cell(50, 8, nettoyer_texte(str(data['credits_valides'])), 1)
    pdf.cell(50, 8, nettoyer_texte(data['decision_jury']), 1)

    pdf.ln(15)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, nettoyer_texte("Ce bulletin est généré automatiquement. Aucun grattage n’est autorisé."), ln=True, align='C')

    os.makedirs("temp", exist_ok=True)
    path = f"temp/Bulletin_{data['matricule']}.pdf"
    pdf.output(path)
    return path
