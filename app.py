import streamlit as st
import pandas as pd
import yfinance as yf
from groq import Groq
from supabase import create_client, Client
from duckduckgo_search import DDGS
import plotly.graph_objects as go
import urllib.parse
import hashlib

# --- 1. CONFIGURATION VISUELLE ---
st.set_page_config(page_title="A&L Commodity Hub", layout="wide", page_icon="🍫")

st.markdown("""
    <style>
    .stApp { background-color: #FDFCFB; }
    .stButton>button { background-color: #D4AF37; color: #4E342E; border-radius: 8px; font-weight: bold; width: 100%; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; border-top: 4px solid #D4AF37; margin-bottom: 10px; color: #4E342E; shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONNEXION API (VÉRIFICATION) ---
try:
    client_ia = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error(f"⚠️ Erreur de configuration des clés : {e}")
    st.stop()

# --- 3. FONCTIONS SYSTÈME ---

def call_ia(prompt):
    try:
        completion = client_ia.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except: return "L'IA ne répond pas. Vérifiez votre clé Groq."

def get_market_price():
    try:
        data = yf.Ticker("CC=F").history(period="1d")
        return round(data['Close'].iloc[-1], 2)
    except: return "Indisponible"

# --- 4. BARRE LATÉRALE ---
st.sidebar.title("🍫 A&L HUB PRO")
st.sidebar.metric("📊 COURS CACAO (ICE)", f"{get_market_price()} $")
continent = st.sidebar.selectbox("🌍 Zone cible", ["Europe", "Asie", "Afrique", "Amérique", "Moyen-Orient"])

menu = ["🚀 Radar RFQ (Chaud)", "🕵️ Identité (OSINT)", "📦 Catalogue", "📂 CRM Leads"]
choice = st.sidebar.selectbox("Menu", menu)

# --- MODULE 1 : RADAR RFQ (MODIFIÉ POUR PLUS DE RÉSULTATS) ---
if choice == "🚀 R
