# auth.py

import streamlit as st
import hashlib
from database import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    hashed = hash_password(password)

    # 🔍 Vérifie si l'utilisateur existe
    cursor.execute("SELECT * FROM utilisateurs WHERE email=%s AND mot_de_passe=%s", (email, hashed))
    user = cursor.fetchone()

    if not user:
        return False

    # 🔁 Si c'est un étudiant, récupérer le matricule lié
    if user["role"] == "etudiant":
        cursor.execute("SELECT matricule FROM etudiants WHERE utilisateur_id = %s", (user["id"],))
        etu = cursor.fetchone()
        user["matricule"] = etu["matricule"] if etu else None
    else:
        user["matricule"] = None

    st.session_state.user = {
        "id": user["id"],
        "nom": user["nom"],
        "email": user["email"],
        "role": user["role"],
        "matricule": user["matricule"]
    }

    cursor.close()
    conn.close()
    return True

def is_authenticated():
    return "user" in st.session_state

def logout():
    st.session_state.pop("user", None)

def create_user_etudiant(nom, email, password, matricule, promotion_id):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    try:
        # 1. Créer dans utilisateurs
        cursor.execute("""
            INSERT INTO utilisateurs (nom, email, mot_de_passe, role) VALUES (%s, %s, %s, 'etudiant')
        """, (nom, email, hashed))
        utilisateur_id = cursor.lastrowid

        # 2. Créer dans etudiants
        cursor.execute("""
            INSERT INTO etudiants (nom, matricule, promotion_id, utilisateur_id)
            VALUES (%s, %s, %s, %s)
        """, (nom, matricule, promotion_id, utilisateur_id))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Erreur lors de la création : {e}")
        return False
    finally:
        cursor.close()
        conn.close()
