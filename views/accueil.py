# views/accueil.py

import streamlit as st
from PIL import Image
import os

def show():
    # Charger le CSS
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # === LOGO UOM EN HAUT ===
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        st.image("assets/logo_uom.png", width=90)
    with col_title:
        st.markdown("<h1 style='margin-bottom:0;'>Université Officielle de Mbujimayi</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>🎓 Plateforme de consultation des résultats</p>", unsafe_allow_html=True)

    # === HERO AVEC BACKGROUND ===
    st.image("assets/uom_hero.jpg", use_container_width=True, caption="Vue du bâtiment principal")

    # === STATISTIQUES / CARTES ===
    st.markdown("<div class='section-cards'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="card stat-card glass">
                <div class="icon-circle bg-blue">🏫</div>
                <h3>Facultés</h3>
                <p>6 Facultés enregistrées</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="card stat-card glass">
                <div class="icon-circle bg-green">👨‍🎓</div>
                <h3>Étudiants</h3>
                <p>+ 2 300 étudiants actifs</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="card stat-card glass">
                <div class="icon-circle bg-orange">📅</div>
                <h3>Année académique</h3>
                <p>2024 - 2025</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # === À PROPOS ===
    st.markdown("<div class='section-about'>", unsafe_allow_html=True)
    col_img, col_text = st.columns(2)
    with col_img:
        st.image("assets/uom_campus.jpg", caption="Bâtiment UOM", use_container_width=True)
    with col_text:
        st.markdown("""
            <h2>📘 À propos de la plateforme</h2>
            <ul>
                <li>🔍 Consultation des résultats en ligne</li>
                <li>📁 Bulletins téléchargeables</li>
                <li>🔐 Espace personnel sécurisé</li>
                <li>📊 Statistiques académiques</li>
            </ul>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # === FONCTIONNALITÉS ===
    st.markdown("<div class='section-features'><h2>✨ Fonctionnalités</h2>", unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.image("assets/search.png", width=60)
        st.markdown("**Recherche rapide**<br><small>Par promotion et faculté.</small>", unsafe_allow_html=True)
    with col_f2:
        st.image("assets/stats.png", width=60)
        st.markdown("**Statistiques visuelles**<br><small>Performances claires.</small>", unsafe_allow_html=True)
    with col_f3:
        st.image("assets/pdf.png", width=60)
        st.markdown("**Téléchargement PDF**<br><small>Bulletin officiel exportable.</small>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # === FOOTER ===
    st.markdown("<div class='footer'><p>© 2025 UOM — Tous droits réservés</p></div>", unsafe_allow_html=True)
