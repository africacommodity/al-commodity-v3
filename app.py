import streamlit as st
import pandas as pd
import yfinance as yf
from groq import Groq
from supabase import create_client, Client
from duckduckgo_search import DDGS
import plotly.graph_objects as go
import urllib.parse
from fpdf import FPDF
import hashlib
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import io

# --- CONFIGURATION VISUELLE PREMIUM ---
st.set_page_config(page_title="A&L Commodity V3 Elite", layout="wide", page_icon="🍫")

st.markdown("""
    <style>
    :root { --main-color: #4E342E; --gold: #D4AF37; }
    .stApp { background-color: #FDFCFB; }
    .stButton>button { background-color: #4E342E; color: #D4AF37; border: 1px solid #D4AF37; border-radius: 8px; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #D4AF37; color: #4E342E; }
    .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #D4AF37; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONNEXION AUX API (SECRETS) ---
try:
    client_ia = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("⚠️ Erreur : Configurez les SECRETS dans Streamlit Cloud.")

# --- MOTEUR DE RECHERCHE ---
B2B_SITES = ["alibaba.com", "indiamart.com", "europages.com", "tradekey.com", "kompass.com", "linkedin.com/posts", "globalsources.com", "turkishexporter.net", "made-in-china.com"]

# --- FONCTIONS SYSTÈME ---
def call_ia(prompt):
    try:
        completion = client_ia.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "system", "content": "Tu es le Directeur Commercial expert de A&L Commodity."},
                      {"role": "user", "content": prompt}],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except: return "L'IA est momentanément indisponible."

def get_gravatar(email):
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=200"

# --- SIDEBAR ---
st.sidebar.title("🍫 A&L GLOBAL HUB")
st.sidebar.markdown("---")
continent = st.sidebar.selectbox("🌍 Zone de Prospection", ["Europe", "Asie", "Afrique", "Moyen-Orient", "Amérique"])

try:
    price_cacao = yf.Ticker("CC=F").history(period="1d")['Close'].iloc[-1]
    st.sidebar.metric("📊 COURS CACAO (ICE)", f"{round(price_cacao, 2)} $")
except:
    st.sidebar.write("Bourse fermée")

menu = ["🚀 RADAR RFQ (Chaud)", "🕵️ DEEP IDENTITY", "📦 CATALOGUE", "📂 CRM & CLOSING", "📉 ANALYSE MARCHÉ"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- MODULES ---
if choice == "🚀 RADAR RFQ (Chaud)":
    st.title(f"🔥 Radar RFQ & LinkedIn - {continent}")
    prod = st.text_input("Produit à tracker (ex: Noix de Cajou)")
    if st.button("🔥 LANCER LA COLLECTE"):
        with st.spinner("Recherche..."):
            query = f'"{prod}" (RFQ OR "buying request") {continent} {" OR ".join([f"site:{s}" for s in B2B_SITES])}'
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=10))
                for r in results:
                    st.markdown(f"""<div class="metric-card"><h4>{r['title']}</h4><p>{r['body']}</p><a href="{r['href']}" target="_blank">Voir l'offre</a></div>""", unsafe_allow_html=True)

elif choice == "🕵️ DEEP IDENTITY":
    st.title("🕵️ Identité & Social Footprint")
    email_t = st.text_input("Email du prospect")
    if st.button("🔍 Scanner"):
        col1, col2 = st.columns([1, 2])
        col1.image(get_gravatar(email_t), width=150)
        with col2:
            with DDGS() as ddgs:
                osint = list(ddgs.text(f'"{email_t}" site:linkedin.com OR site:facebook.com', max_results=5))
                st.info(call_ia(f"Analyse cet email et trouve les liens sociaux : {str(osint)}"))

elif choice == "📦 CATALOGUE":
    st.title("📦 Mon Catalogue Produits")
    with st.form("p_form"):
        n = st.text_input("Nom")
        o = st.text_input("Origine")
        p = st.number_input("Prix $/T")
        if st.form_submit_button("Enregistrer"):
            supabase.table("products").insert({"name": n, "origin": o, "price_ref": p}).execute()
            st.success("Produit ajouté !")

elif choice == "📂 CRM & CLOSING":
    st.title("📂 Gestionnaire de Leads")
    leads = supabase.table("leads").select("*").execute().data
    if leads:
        for l in leads:
            with st.expander(f"🏢 {l['company_name']}"):
                st.write(f"Email: {l['email']}")
                if st.button("📲 WhatsApp", key=l['id']):
                    st.write("Ouverture WhatsApp...")

elif choice == "📉 ANALYSE MARCHÉ":
    st.title("📈 Tendances & Marché")
    hist = yf.Ticker("CC=F").history(period="60d")
    fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#D4AF37'))])
    st.plotly_chart(fig, use_container_width=True)
