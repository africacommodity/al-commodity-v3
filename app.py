import streamlit as st
import pandas as pd
import yfinance as yf
from groq import Groq
from supabase import create_client, Client
from duckduckgo_search import DDGS
import plotly.graph_objects as go
import hashlib

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="A&L Hub", layout="wide")

# --- 2. CONNEXION API ---
try:
    client_ia = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Erreur de cles API dans les Secrets.")
    st.stop()

# --- 3. BARRE LATERALE ---
st.sidebar.title("🍫 A&L HUB PRO")
menu = ["Radar", "OSINT", "Catalogue", "CRM"]
choice = st.sidebar.selectbox("Menu", menu)

# --- 4. MODULE RADAR (RECHERCHE) ---
if choice == "Radar":
    st.title("🚀 Radar de Prospection")
    prod = st.text_input("Produit (ex: Cocoa beans)")
    
    if st.button("Lancer la recherche"):
        if prod:
            with st.spinner("Recherche..."):
                try:
                    with DDGS() as ddgs:
                        # Requete simplifiee pour eviter les erreurs
                        res = list(ddgs.text(f"{prod} buying request", max_results=10))
                        if res:
                            for r in res:
                                st.markdown(f"**{r['title']}**")
                                st.write(r['body'])
                                st.write(f"[Lien]({r['href']})")
                                st.divider()
                        else:
                            st.info("Aucun resultat. Essayez un mot en anglais.")
                except Exception as e:
                    st.error(f"Erreur recherche: {e}")

# --- 5. MODULE CATALOGUE (TEST SUPABASE) ---
elif choice == "Catalogue":
    st.title("📦 Mon Catalogue")
    with st.form("add_p"):
        n = st.text_input("Produit")
        o = st.text_input("Origine")
        p = st.number_input("Prix $/T")
        if st.form_submit_button("Enregistrer"):
            try:
                supabase.table("products").insert({"name": n, "origin": o, "price_ref": p}).execute()
                st.success("Enregistre dans Supabase !")
            except Exception as e:
                st.error(f"Erreur Supabase: {e}")

# --- 6. MODULE CRM ---
elif choice == "CRM":
    st.title("📂 Gestion Leads")
    try:
        leads = supabase.table("leads").select("*").execute().data
        if leads:
            st.table(pd.DataFrame(leads))
        else:
            st.info("Le CRM est vide.")
    except Exception as e:
        st.error(f"Erreur CRM: {e}")

# --- 7. MODULE OSINT ---
elif choice == "OSINT":
    st.title("🕵️ Identification")
    email = st.text_input("Email prospect")
    if st.button("Scanner"):
        st.write(f"Recherche pour {email}...")
        with DDGS() as ddgs:
            social = list(ddgs.text(f'"{email}" site:linkedin.co
