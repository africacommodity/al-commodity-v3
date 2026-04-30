import streamlit as st
import pandas as pd
import yfinance as yf
from groq import Groq
from supabase import create_client
from duckduckgo_search import DDGS

# 1. SETUP
st.set_page_config(page_title="AL HUB")

# 2. CLES API
try:
    k = st.secrets["GROQ_API_KEY"]
    u = st.secrets["SUPABASE_URL"]
    s = st.secrets["SUPABASE_KEY"]
    client_ia = Groq(api_key=k)
    supabase = create_client(u, s)
except:
    st.error("Erreur de cles dans Secrets")
    st.stop()

# 3. MENU
menu = ["Radar", "Catalogue", "CRM"]
choice = st.sidebar.radio("Navigation", menu)

# 4. MODULE RADAR
if choice == "Radar":
    st.title("Radar de Prospection")
    prod = st.text_input("Produit (anglais):")
    if st.button("Lancer"):
        if prod:
            with st.spinner("Recherche..."):
                try:
                    with DDGS() as ddgs:
                        res = list(ddgs.text(prod, max_results=5))
                        if res:
                            for r in res:
                                st.markdown(f"**{r['title']}**")
                                st.write(r['body'])
                                st.write(r['href'])
                                st.write("---")
                        else:
                            st.write("Aucun resultat")
                except Exception as e:
                    st.error("Erreur recherche")

# 5. MODULE CATALOGUE
elif choice == "Catalogue":
    st.title("Catalogue")
    with st.form("f1"):
        n = st.text_input("Nom")
        p = st.number_input("Prix")
        if st.form_submit_button("Enregistrer"):
            try:
                supabase.table("products").insert({"name":n,"price_ref":p}).execute()
                st.success("Enregistre !")
            except:
                st.error("Erreur base de donnees")

# 6. MODULE CRM
elif choice == "CRM":
    st.title("CRM")
    try:
        leads = supabase.table("leads").select("*").execute().data
        if leads:
            st.write(pd.DataFrame(leads))
        else:
            st.write("Vide")
    except:
        st.error("Erreur CRM")
