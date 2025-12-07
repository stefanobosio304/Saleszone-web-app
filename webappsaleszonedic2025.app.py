import streamlit as st
import subprocess
import sys
import pandas as pd
import numpy as np
import io
from io import BytesIO

# ==============================================================================
# 1. CONFIGURAZIONE PAGINA (OBBLIGATORIO: PRIMA ISTRUZIONE)
# ==============================================================================
st.set_page_config(
    page_title="Saleszone | Suite Operativa",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. BLOCCO DI AUTO-RIPARAZIONE (INSTALLAZIONE DIPENDENZE)
# ==============================================================================
# Questo codice controlla se openpyxl esiste. Se manca, lo scarica e lo installa.
try:
    import openpyxl
except ImportError:
    st.warning("⚠️ Rilevata mancanza di openpyxl. Sto installando la libreria mancante...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
        import openpyxl
        st.success("✅ Installazione completata! Se vedi ancora errori, ricarica la pagina.")
    except Exception as e:
        st.error(f"Errore durante l'installazione automatica: {e}")

# ==============================================================================
# 3. STILE E BRANDING (CSS)
# ==============================================================================
def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            color: #2940A8;
        }
        [data-testid="stSidebar"] {
            background-color: #F4F6FC;
            border-right: 1px solid #DBDBDB;
        }
        h1, h2, h3 {
            color: #2940A8 !important;
            font-weight: 700;
        }
        div.stButton > button:first-child {
            background-color: #FA7838;
            color: white;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            padding: 0.5rem 1rem;
        }
        div.stButton > button:first-child:hover {
            background-color: #e06020;
            color: white;
        }
        [data-testid="stMetricValue"] {
            color: #FA7838 !important;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            color: #2940A8 !important;
        }
        .sidebar-logo {
            font-size: 28px;
            font-weight: 800;
            color: #2940A8;
            margin-bottom: 20px;
        }
        .sidebar-logo span {
            color: #FA7838;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==============================================================================
# 4. UTILITIES E FUNZIONI GLOBALI
# ==============================================================================

def load_data(file):
    """Carica CSV o Excel gestendo errori comuni di formattazione."""
    if file is None: return None
    try:
        if file.name.endswith('.csv'):
            try:
                df = pd.read_csv(file, encoding='utf-8')
                if df.shape[1] < 2:
                    file.seek(0)
                    df = pd.read_csv(file, sep=';', encoding='utf-8')
            except:
                file.seek(0)
                df = pd.read_csv(file, sep=';', encoding='latin1')
        else:
            # Qui usiamo openpyxl esplicitamente
            df = pd.read_excel(file, engine='openpyxl')
        
        # Pulizia base colonne
        df.columns = df.columns.str.strip()
        df.columns = [c.replace("\ufeff", "") for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")
        return None

def download_excel(dfs_dict, filename):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        for sheet_name, df in dfs_dict.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    
    st.download_button(
        label=f"📥 Scarica {filename}",
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==============================================================================
# 5. PAGINE (HOME, PPC, BRAND ANALYTICS...)
# ==============================================================================

def show_home():
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
        <div style='background-color: #2940A8; padding: 20px; border-radius: 10px; text-align: center;'>
            <h1 style='color: white !important; margin: 0; font-size: 50px;'>S<span style='color: #FA7838;'>Z</span></h1>
            <p style='color: white; margin: 0; font-size: 12px; letter-spacing: 2px;'>SALESZONE</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.title("Benvenuto in Saleszone")
        st.markdown("**Il tuo spazio di crescita su Amazon.**")
        st.write("""
        Questa suite di strumenti è progettata per ottimizzare le tue performance, analizzare i dati
        e semplificare la gestione del tuo account Amazon Seller.
        """)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("🎯 **Missione**\n\nAiutare i brand a crescere su Amazon attraverso una consulenza strategica.")
    with c2:
        st.success("💎 **Valori**\n\nProfessionalità, Autenticità, Trasparenza, Disciplina, Risultati Concreti.")
    with c3:
        st.warning("🤝 **Approccio**\n\nSupporto continuo one-to-one. Niente filtri, niente intermediari.")

def show_ppc_optimizer():
    st.title("📊 PPC Ads Optimizer")
    st.markdown("Analisi KPI, Search Terms e ottimizzazione bid.")

    col1, col2 = st.columns(2)
    with col1:
        st_file = st.file_uploader("Report Search Term (CSV/XLSX)", type=["csv", "xlsx"])
    with col2:
        acos_target = st.number_input("ACOS Target (%)", 1, 100, 30)
        click_threshold = st.number_input("Click minimi senza vendite", 1, 50, 10)

    if st_file:
        df = load_data(st_file)
        if df is None: return

        col_map = {
            'Targeting': 'Keyword', 'Termine ricerca cliente': 'Search Term', 
            'Customer Search Term': 'Search Term', 'Impressioni': 'Impressions', 
            'Clic': 'Clicks', 'Spesa': 'Spend', 'Vendite totali (€) 7 giorni': 'Sales', 
            '7 Day Total Sales': 'Sales', 'Totale ordini (#) 7 giorni': 'Orders', 
            '7 Day Total Orders': 'Orders', 'Nome campagna': 'Campaign', 'Nome portafoglio': 'Portfolio'
        }
        df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)
        
        required = ['Impressions', 'Clicks', 'Spend', 'Sales', 'Orders']
        if not all(col in df.columns for col in required):
            st.error(f"Colonne mancanti. Assicurati che il file abbia: {required}")
            return

        for c in required: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
        df['ACOS'] = df.apply(lambda x: (x['Spend']/x['Sales']*100) if x['Sales'] > 0 else 0, axis=1)
        df['ROAS'] = df.apply(lambda x: (x['Sales']/x['Spend']) if x['Spend'] > 0 else 0, axis=1)
        df['CTR'] = (df['Clicks'] / df['Impressions'] * 100).fillna(0)
        df['CPC'] = (df['Spend'] / df['Clicks']).fillna(0)

        tot_spend = df['Spend'].sum()
        tot_sales = df['Sales'].sum()
        tot_acos = (tot_spend/tot_sales*100) if tot_sales > 0 else 0
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Spesa Totale", f"€ {tot_spend:,.2f}")
        k2.metric("Vendite Totali", f"€ {tot_sales:,.2f}")
        k3.metric("ACOS Globale", f"{tot_acos:.2f}%")
        k4.metric("ROAS Globale", f"{tot_sales/tot_spend:.2f}" if tot_spend > 0 else "0")

        st.divider()
        st.subheader("🩸 Termini 'Sanguinanti'")
        bleeding = df[(df['Sales'] == 0) & (df['Clicks'] >= click_threshold)].sort_values(by='Spend', ascending=False)
        st.dataframe(bleeding[['Campaign', 'Keyword', 'Search Term', 'Clicks', 'Spend', 'CPC']].style.format({'Spend': '€{:.2f}', 'CPC': '€{:.2f}'}), use_container_width=True)
        
        st.subheader("⭐ Termini Vincenti")
        winners = df[(df['Sales'] > 0) & (df['ACOS'] < acos_target)].sort_values(by='Sales', ascending=False)
        st.dataframe(winners[['Campaign', 'Search Term', 'Sales', 'ACOS', 'ROAS']].style.format({'Sales': '€{:.2f}', 'ACOS': '{:.2f}%', 'ROAS': '{:.2f}'}), use_container_width=True)

def show_brand_analytics():
    st.title("📈 Brand Analytics Insights")
    ba_file = st.file_uploader("Carica CSV Brand Analytics", type=["csv"])
    if ba_file:
        df = load_data(ba_file)
        if df is None: return 
        
        # Mappatura semplice
        map_ba = {}
        for c in df.columns:
            cl = c.lower()
            if 'volume' in cl: map_ba['Volume'] = c
            elif 'query' in cl: map_ba['Query'] = c
            elif 'totale' in cl and 'clic' in cl: map_ba['Click Tot'] = c
            elif 'totale' in cl and 'impressioni' in cl: map_ba['Impressioni Tot'] = c
            elif 'marchio' in cl and 'clic' in cl: map_ba['Click Brand'] = c
            elif 'marchio' in cl and 'impressioni' in cl: map_ba['Impressioni Brand'] = c
            elif 'marchio' in cl and 'acquisti' in cl: map_ba['Acquisti Brand'] = c
            elif 'totale' in cl and 'acquisti' in cl: map_ba['Acquisti Tot'] = c

        if 'Query' not in map_ba:
            st.error("Colonne non riconosciute.")
            return

        data = pd.DataFrame()
        data['Query'] = df[map_ba['Query']]
        data['Volume'] = pd.to_numeric(df[map_ba.get('Volume', df.columns[1])], errors='coerce').fillna(0)
        
        # Calcoli semplici per evitare errori
        imp_tot = pd.to_numeric(df[map_ba.get('Impressioni Tot')], errors='coerce').fillna(0) if 'Impressioni Tot' in map_ba else 1
        imp_brand = pd.to_numeric(df[map_ba.get('Impressioni Brand')], errors='coerce').fillna(0) if 'Impressioni Brand' in map_ba else 0
        data['Impression Share'] = (imp_brand / imp_tot * 100).fillna(0)
        
        st.dataframe(data.sort_values(by='Volume', ascending=False).head(50), use_container_width=True)
        download_excel({"Brand Analytics": data}, "ba_saleszone.xlsx")

def show_sqp():
    st.title("🔎 Search Query Performance")
    sqp_file = st.file_uploader("Carica report SQP (CSV)", type=['csv'])
    if sqp_file:
        df = load_data(sqp_file)
        if df is None: return
        st.write("Anteprima dati:", df.head())

def show_inventory():
    st.title("📦 Controllo Inventario FBA")
    inv_file = st.file_uploader("Carica Inventory Ledger", type=['csv', 'xlsx'])
    if inv_file:
        df = load_data(inv_file)
        if df is None: return
        
        df.columns = [c.lower() for c in df.columns]
        # Logica base per evitare crash se colonne mancano
        st.write("Colonne trovate:", list(df.columns))
        st.info("Funzionalità base attiva. Caricare file standard Amazon.")

def show_funnel_audit():
    st.title("🧭 Funnel Audit")
    macro_file = st.file_uploader("Carica File Macro Campagne", type=['xlsx', 'csv'])
    if macro_file:
        df = load_data(macro_file)
        if df is None: return
        st.write("File caricato correttamente.")

def show_invoices():
    st.title("📄 Generazione Corrispettivi")
    file = st.file_uploader("Carica Report Transazioni (CSV)", type=['csv'])
    if file:
        df = load_data(file)
        if df is None: return
        st.write("File caricato correttamente.")

# ==============================================================================
# 6. MENU NAVIGAZIONE
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("<div class='sidebar-logo'>S<span>Z</span> SALESZONE</div>", unsafe_allow_html=True)
        selected = st.radio(
            "Strumenti",
            ["Home", "PPC Optimizer", "Brand Analytics", "SQP Analysis", "Inventario FBA", "Funnel Audit", "Corrispettivi"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.caption("© 2025 Saleszone Agency")

    if selected == "Home": show_home()
    elif selected == "PPC Optimizer": show_ppc_optimizer()
    elif selected == "Brand Analytics": show_brand_analytics()
    elif selected == "SQP Analysis": show_sqp()
    elif selected == "Inventario FBA": show_inventory()
    elif selected == "Funnel Audit": show_funnel_audit()
    elif selected == "Corrispettivi": show_invoices()

if __name__ == "__main__":
    main()
