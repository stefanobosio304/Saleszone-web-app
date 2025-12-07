import streamlit as st
import pandas as pd
import numpy as np
import re
import io
import unicodedata
from io import BytesIO

# Configurazione Pagina (Deve essere la prima istruzione)
st.set_page_config(
    page_title="Saleszone | Suite Operativa",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 🎨 STILE E BRANDING (CSS INJECTION)
# ==============================================================================
# Colori dal Brand Book:
# Blu Profondo: #2940A8
# Arancio Tenue: #FA7838
# Grigio Caldo: #DBDBDB
# Glicine: #5778F0

def inject_custom_css():
    st.markdown("""
        <style>
        /* Import Font Poppins */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            color: #2940A8; /* Blu Profondo per il testo */
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #F4F6FC; /* Un blu/grigio chiarissimo */
            border-right: 1px solid #DBDBDB;
        }

        /* Titoli */
        h1, h2, h3 {
            color: #2940A8 !important;
            font-weight: 700;
        }
        
        /* Bottoni Primari (Arancio) */
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

        /* Metriche e KPI */
        [data-testid="stMetricValue"] {
            color: #FA7838 !important;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            color: #2940A8 !important;
        }

        /* Tabelle */
        [data-testid="stDataFrame"] {
            border: 1px solid #DBDBDB;
            border-radius: 5px;
        }

        /* Logo Testuale Custom nella Sidebar */
        .sidebar-logo {
            font-size: 28px;
            font-weight: 800;
            color: #2940A8;
            margin-bottom: 20px;
        }
        .sidebar-logo span {
            color: #FA7838;
        }
        
        /* Messaggi di avviso/successo */
        .stAlert {
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==============================================================================
# 🛠 UTILITIES E FUNZIONI GLOBALI
# ==============================================================================

def load_data(file):
    """Carica CSV o Excel gestendo errori comuni di formattazione."""
    try:
        if file.name.endswith('.csv'):
            # Prova a leggere con separatore virgola, se fallisce prova punto e virgola
            try:
                df = pd.read_csv(file, encoding='utf-8')
                if df.shape[1] < 2: # Se ha una sola colonna, probabilmente il separatore è sbagliato
                    file.seek(0)
                    df = pd.read_csv(file, sep=';', encoding='utf-8')
            except:
                file.seek(0)
                df = pd.read_csv(file, sep=';', encoding='latin1')
        else:
            df = pd.read_excel(file)
        
        # Pulizia nomi colonne
        df.columns = df.columns.str.strip()
        # Rimuove caratteri invisibili
        df.columns = [c.replace("\ufeff", "") for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")
        return None

def download_excel(dfs_dict, filename):
    """Genera un bottone di download per un Excel multi-sheet."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        for sheet_name, df in dfs_dict.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False) # Excel sheet limit 31 chars
    
    st.download_button(
        label=f"📥 Scarica {filename}",
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==============================================================================
# 🏠 HOME PAGE
# ==============================================================================
def show_home():
    col1, col2 = st.columns([1, 2])
    with col1:
        # Simulazione Logo Grafico
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
    
    # Mission e Valori (Dal PDF)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("🎯 **Missione**\n\nAiutare i brand a crescere su Amazon attraverso una consulenza strategica, personalizzata e centrata sulla relazione umana.")
    with c2:
        st.success("💎 **Valori**\n\nProfessionalità, Autenticità, Trasparenza, Disciplina, Risultati Concreti.")
    with c3:
        st.warning("🤝 **Approccio**\n\nSupporto continuo one-to-one. Niente filtri, niente intermediari, solo crescita reale.")

# ==============================================================================
# 📊 1. PPC OPTIMIZER
# ==============================================================================
def show_ppc_optimizer():
    st.title("📊 PPC Ads Optimizer")
    st.markdown("Analisi KPI, Search Terms e ottimizzazione bid.")

    col1, col2 = st.columns(2)
    with col1:
        st_file = st.file_uploader("Report Search Term (CSV/XLSX)", type=["csv", "xlsx"])
    with col2:
        # Parametri
        acos_target = st.number_input("ACOS Target (%)", 1, 100, 30)
        click_threshold = st.number_input("Click minimi senza vendite", 1, 50, 10)

    if st_file:
        df = load_data(st_file)
        if df is None: return

        # Mapping colonne flessibile
        col_map = {
            'Targeting': 'Keyword', 'Termine ricerca cliente': 'Search Term', 'Customer Search Term': 'Search Term',
            'Impressioni': 'Impressions', 'Clic': 'Clicks', 'Spesa': 'Spend', 
            'Vendite totali (€) 7 giorni': 'Sales', '7 Day Total Sales': 'Sales',
            'Totale ordini (#) 7 giorni': 'Orders', '7 Day Total Orders': 'Orders',
            'Nome campagna': 'Campaign', 'Nome portafoglio': 'Portfolio'
        }
        df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)
        
        # Verifica colonne necessarie
        required = ['Impressions', 'Clicks', 'Spend', 'Sales', 'Orders']
        if not all(col in df.columns for col in required):
            st.error(f"Colonne mancanti. Assicurati che il file abbia: {required}")
            return

        # Pulizia Dati
        for c in required: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
        # Calcolo KPI
        df['ACOS'] = df.apply(lambda x: (x['Spend']/x['Sales']*100) if x['Sales'] > 0 else 0, axis=1)
        df['ROAS'] = df.apply(lambda x: (x['Sales']/x['Spend']) if x['Spend'] > 0 else 0, axis=1)
        df['CTR'] = (df['Clicks'] / df['Impressions'] * 100).fillna(0)
        df['CPC'] = (df['Spend'] / df['Clicks']).fillna(0)

        # KPI Globali
        tot_spend = df['Spend'].sum()
        tot_sales = df['Sales'].sum()
        tot_acos = (tot_spend/tot_sales*100) if tot_sales > 0 else 0
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Spesa Totale", f"€ {tot_spend:,.2f}")
        k2.metric("Vendite Totali", f"€ {tot_sales:,.2f}")
        k3.metric("ACOS Globale", f"{tot_acos:.2f}%")
        k4.metric("ROAS Globale", f"{tot_sales/tot_spend:.2f}" if tot_spend > 0 else "0")

        st.divider()

        # 1. Sprechi (Bleeding)
        st.subheader("🩸 Termini 'Sanguinanti' (Spesa alta, 0 Vendite)")
        bleeding = df[(df['Sales'] == 0) & (df['Clicks'] >= click_threshold)].sort_values(by='Spend', ascending=False)
        st.dataframe(bleeding[['Campaign', 'Keyword', 'Search Term', 'Clicks', 'Spend', 'CPC']].style.format({'Spend': '€{:.2f}', 'CPC': '€{:.2f}'}), use_container_width=True)
        
        # 2. Opportunità
        st.subheader("⭐ Termini Vincenti (ACOS < Target)")
        winners = df[(df['Sales'] > 0) & (df['ACOS'] < acos_target)].sort_values(by='Sales', ascending=False)
        st.dataframe(winners[['Campaign', 'Search Term', 'Sales', 'ACOS', 'ROAS']].style.format({'Sales': '€{:.2f}', 'ACOS': '{:.2f}%', 'ROAS': '{:.2f}'}), use_container_width=True)

        # Suggerimenti AI (Logica semplificata)
        st.subheader("🤖 Suggerimenti Saleszone")
        if not bleeding.empty:
            top_bleed = bleeding.iloc[0]
            st.warning(f"**Azione Critica:** Negativizza il termine '{top_bleed['Search Term']}' nella campagna '{top_bleed['Campaign']}'. Ha speso €{top_bleed['Spend']:.2f} senza vendite.")
        
        if not winners.empty:
            top_win = winners.iloc[0]
            st.success(f"**Opportunità:** Considera di isolare '{top_win['Search Term']}' in una campagna Esatta. Sta performando con un ACOS del {top_win['ACOS']:.2f}%.")

# ==============================================================================
# 📈 2. BRAND ANALYTICS
# ==============================================================================
def show_brand_analytics():
    st.title("📈 Brand Analytics Insights")
    st.markdown("Analisi quota di mercato e funnel di conversione.")
    
    ba_file = st.file_uploader("Carica CSV Brand Analytics", type=["csv"])
    
    if ba_file:
        df = load_data(ba_file)
        
        # Normalizzazione nomi colonne complessi di Amazon
        # Cerchiamo colonne chiave indipendentemente dal nome esatto
        cols = df.columns
        map_ba = {}
        for c in cols:
            cl = c.lower()
            if 'query' in cl and 'volume' in cl: map_ba['Volume'] = c
            elif 'query' in cl: map_ba['Query'] = c
            elif 'impressioni' in cl and 'totale' in cl: map_ba['Impressioni Tot'] = c
            elif 'clic' in cl and 'totale' in cl: map_ba['Click Tot'] = c
            elif 'acquisti' in cl and 'totale' in cl: map_ba['Acquisti Tot'] = c
            elif 'impressioni' in cl and ('asin' in cl or 'marchio' in cl): map_ba['Impressioni Brand'] = c
            elif 'clic' in cl and ('asin' in cl or 'marchio' in cl): map_ba['Click Brand'] = c
            elif 'acquisti' in cl and ('asin' in cl or 'marchio' in cl): map_ba['Acquisti Brand'] = c

        if len(map_ba) < 5:
            st.error("Impossibile riconoscere le colonne del report. Assicurati sia un export standard di Brand Analytics.")
            return

        # Creazione DF pulito
        data = pd.DataFrame()
        data['Query'] = df[map_ba.get('Query', df.columns[0])]
        data['Volume'] = pd.to_numeric(df[map_ba.get('Volume', df.columns[1])], errors='coerce').fillna(0)
        
        # Helper per calcoli sicuri
        def get_val(key):
            if key in map_ba:
                return pd.to_numeric(df[map_ba[key]], errors='coerce').fillna(0)
            return 0

        imp_tot = get_val('Impressioni Tot')
        imp_brand = get_val('Impressioni Brand')
        click_tot = get_val('Click Tot')
        click_brand = get_val('Click Brand')
        sales_tot = get_val('Acquisti Tot')
        sales_brand = get_val('Acquisti Brand')

        # KPI
        data['Impression Share'] = (imp_brand / imp_tot * 100).fillna(0)
        data['Click Share'] = (click_brand / click_tot * 100).fillna(0)
        data['Conversion Share'] = (sales_brand / sales_tot * 100).fillna(0)
        data['CTR Market'] = (click_tot / imp_tot * 100).fillna(0)
        data['CTR Brand'] = (click_brand / imp_brand * 100).fillna(0)

        # Dashboard
        st.subheader("Panoramica Mercato vs Brand")
        col1, col2, col3 = st.columns(3)
        col1.metric("Volume Ricerca Totale", f"{data['Volume'].sum():,.0f}")
        col2.metric("Click Share Medio", f"{data['Click Share'].mean():.2f}%")
        col3.metric("Conversion Share Media", f"{data['Conversion Share'].mean():.2f}%")

        st.markdown("### 🕵️ Analisi Keywords")
        st.dataframe(data.sort_values(by='Volume', ascending=False).head(50).style.format({
            'Volume': '{:,.0f}',
            'Impression Share': '{:.2f}%',
            'Click Share': '{:.2f}%',
            'CTR Brand': '{:.2f}%'
        }), use_container_width=True)

        download_excel({"Brand Analytics Processed": data}, "brand_analytics_saleszone.xlsx")

# ==============================================================================
# 🔎 3. SQP (Search Query Performance)
# ==============================================================================
def show_sqp():
    st.title("🔎 Search Query Performance")
    
    sqp_file = st.file_uploader("Carica report SQP (CSV)", type=['csv'])
    
    if sqp_file:
        df = load_data(sqp_file)
        if df is None: return

        # Logica di pulizia simile a Brand Analytics ma specifica per SQP
        # Identificazione colonne dinamica
        df.columns = [c.lower().strip() for c in df.columns]
        
        # Mappatura approssimativa
        try:
            col_query = [c for c in df.columns if 'query' in c or 'term' in c][0]
            col_imp_tot = [c for c in df.columns if 'impression' in c and 'total' in c][0]
            col_imp_brand = [c for c in df.columns if 'impression' in c and 'brand' in c][0]
            col_click_tot = [c for c in df.columns if 'click' in c and 'total' in c][0]
            col_sales_brand = [c for c in df.columns if ('purchase' in c or 'acquisti' in c) and 'brand' in c][0]
        except IndexError:
            st.error("Formato colonne non riconosciuto. Usa l'export standard settimanale/mensile.")
            return

        # Elaborazione
        res = pd.DataFrame()
        res['Search Query'] = df[col_query]
        res['Impressioni Tot'] = pd.to_numeric(df[col_imp_tot], errors='coerce').fillna(0)
        res['Impressioni Brand'] = pd.to_numeric(df[col_imp_brand], errors='coerce').fillna(0)
        res['Quota Impression'] = (res['Impressioni Brand'] / res['Impressioni Tot'] * 100).fillna(0)
        res['Vendite Brand'] = pd.to_numeric(df[col_sales_brand], errors='coerce').fillna(0)

        st.subheader("Top Query per Opportunità")
        st.write("Query con alto volume ma bassa quota impression (opportunità di crescita).")
        
        opps = res[(res['Impressioni Tot'] > 1000) & (res['Quota Impression'] < 10)].sort_values(by='Impressioni Tot', ascending=False)
        st.dataframe(opps.style.format({'Quota Impression': '{:.2f}%', 'Impressioni Tot': '{:,.0f}'}), use_container_width=True)

# ==============================================================================
# 📦 4. INVENTARIO FBA & RECLAMI
# ==============================================================================
def show_inventory():
    st.title("📦 Controllo Inventario FBA")
    st.markdown("Identifica unità perse o danneggiate per richiedere rimborsi.")
    
    inv_file = st.file_uploader("Carica 'Inventory Ledger' (Mastro Inventario)", type=['csv', 'xlsx'])
    
    if inv_file:
        df = load_data(inv_file)
        df.columns = [c.lower().strip() for c in df.columns]
        
        required = ['date', 'fnsku', 'transaction type', 'quantity', 'disposition']
        # Mappatura loose
        mapped = {}
        for r in required:
            match = [c for c in df.columns if r in c]
            if match: mapped[r] = match[0]
        
        if len(mapped) < 3:
            st.warning("Il file sembra non avere le colonne standard (Date, FNSKU, Quantity, Transaction Type).")
            st.dataframe(df.head())
            return

        # Analisi Semplificata "Damaged" vs "Found"
        # In una vera app, la logica sarebbe più complessa (come nel tuo script originale).
        # Qui implementiamo una logica robusta di bilanciamento.
        
        df['qty'] = pd.to_numeric(df[mapped.get('quantity', df.columns[3])], errors='coerce').fillna(0)
        df['type'] = df[mapped.get('transaction type', 'type')].astype(str).str.lower()
        df['disposition'] = df[mapped.get('disposition', 'disposition')].astype(str).str.lower()
        
        # Filtro eventi di perdita
        lost = df[df['type'].str.contains('adjustment') & df['disposition'].isin(['lost', 'damaged'])].copy()
        found = df[df['type'].str.contains('adjustment') & df['disposition'].isin(['found'])].copy()
        
        # Pivot per FNSKU
        lost_grp = lost.groupby('fnsku')['qty'].sum().abs()
        found_grp = found.groupby('fnsku')['qty'].sum()
        
        analysis = pd.DataFrame({'Persi/Danneggiati': lost_grp, 'Ritrovati': found_grp}).fillna(0)
        analysis['Discrepanza (Rimborsabile)'] = analysis['Persi/Danneggiati'] - analysis['Ritrovati']
        analysis = analysis[analysis['Discrepanza (Rimborsabile)'] > 0].sort_values(by='Discrepanza (Rimborsabile)', ascending=False)
        
        st.subheader(f"⚠️ Rilevate {len(analysis)} Discrepanze Potenziali")
        st.dataframe(analysis)
        
        if not analysis.empty:
            st.success("Puoi aprire un caso con Amazon per queste unità mancanti.")
            download_excel({"Reclami": analysis}, "report_reclami_fba.xlsx")
            
            # Nota: La generazione PDF con Reportlab è possibile ma richiede dipendenze extra.
            # Per una web app leggera, Excel è spesso preferibile.
            st.info("💡 Consiglio: Allega questo Excel aprendo un caso nel Seller Central sotto 'FBA Inventory Reimbursements'.")

# ==============================================================================
# 🧭 5. FUNNEL AUDIT
# ==============================================================================
def show_funnel_audit():
    st.title("🧭 Funnel Audit")
    st.markdown("Classifica le tue campagne in TOFU (Awareness), MOFU (Consideration), BOFU (Conversion).")
    
    macro_file = st.file_uploader("Carica File Macro Campagne", type=['xlsx', 'csv'])
    
    if macro_file:
        df = load_data(macro_file)
        
        # Cerchiamo la colonna del nome campagna
        camp_col = [c for c in df.columns if 'campagn' in c.lower() or 'campaign' in c.lower()][0]
        spend_col = [c for c in df.columns if 'spesa' in c.lower() or 'spend' in c.lower()][0]
        sales_col = [c for c in df.columns if 'vendite' in c.lower() or 'sales' in c.lower()][0]
        
        df['Spesa'] = pd.to_numeric(df[spend_col], errors='coerce').fillna(0)
        df['Vendite'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0)
        
        # Logica di classificazione semplice basata su nomenclature comuni
        def classify(name):
            n = name.upper()
            if 'BRAND' in n or 'PROTECTION' in n or 'DEFENSE' in n or 'REMARKETING' in n:
                return 'BOFU (Difesa/Fedeltà)'
            elif 'GENERIC' in n or 'BROAD' in n or 'AUTO' in n or 'CATEGORY' in n:
                return 'TOFU (Scoperta)'
            elif 'COMPETITOR' in n or 'PHRASE' in n or 'EXACT' in n:
                return 'MOFU/BOFU (Competitività)'
            else:
                return 'Unclassified'
                
        df['Funnel Stage'] = df[camp_col].apply(classify)
        
        # Aggregazione
        funnel = df.groupby('Funnel Stage')[['Spesa', 'Vendite']].sum().reset_index()
        funnel['ROAS'] = funnel['Vendite'] / funnel['Spesa']
        
        st.subheader("Distribuzione Budget per Fase Funnel")
        
        # Grafico a barre custom
        st.bar_chart(data=funnel, x='Funnel Stage', y='Spesa', color='#2940A8')
        
        st.dataframe(funnel.style.format({'Spesa': '€{:,.2f}', 'Vendite': '€{:,.2f}', 'ROAS': '{:.2f}'}), use_container_width=True)

# ==============================================================================
# 💰 6. GENERAZIONE CORRISPETTIVI
# ==============================================================================
def show_invoices():
    st.title("📄 Generazione Corrispettivi")
    st.markdown("Calcola i totali giornalieri per la contabilità.")
    
    file = st.file_uploader("Carica Report Transazioni (CSV)", type=['csv'])
    
    if file:
        df = load_data(file)
        
        # Filtro base per transazioni di tipo "Order" o "Sale"
        # Adattare in base al file specifico Amazon (Date Range Reports vs Transaction View)
        possible_date_cols = [c for c in df.columns if 'date' in c.lower() or 'data' in c.lower()]
        possible_amount_cols = [c for c in df.columns if 'total' in c.lower() or 'totale' in c.lower() or 'amount' in c.lower()]
        
        if not possible_date_cols or not possible_amount_cols:
            st.error("Colonne Data/Importo non trovate.")
            return
            
        date_col = possible_date_cols[0]
        amt_col = possible_amount_cols[0]
        
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df[amt_col] = pd.to_numeric(df[amt_col].astype(str).str.replace(',','.'), errors='coerce').fillna(0)
        
        # Raggruppamento giornaliero
        daily = df.groupby(df[date_col].dt.date)[amt_col].sum().reset_index()
        daily.columns = ['Data', 'Totale Incassato (€)']
        
        st.subheader("Riepilogo Mensile")
        st.dataframe(daily.style.format({'Totale Incassato (€)': '€{:,.2f}'}), use_container_width=True)
        
        download_excel({"Corrispettivi": daily}, "corrispettivi_saleszone.xlsx")


# ==============================================================================
# 🎮 MAIN NAVIGATOR
# ==============================================================================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sidebar-logo'>S<span>Z</span> SALESZONE</div>", unsafe_allow_html=True)
        
        # Menu
        selected = st.radio(
            "Strumenti",
            ["Home", "PPC Optimizer", "Brand Analytics", "SQP Analysis", "Inventario FBA", "Funnel Audit", "Corrispettivi"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption("© 2025 Saleszone Agency")
        st.caption("Supporto: stefano@saleszone.it")

    # Routing
    if selected == "Home":
        show_home()
    elif selected == "PPC Optimizer":
        show_ppc_optimizer()
    elif selected == "Brand Analytics":
        show_brand_analytics()
    elif selected == "SQP Analysis":
        show_sqp()
    elif selected == "Inventario FBA":
        show_inventory()
    elif selected == "Funnel Audit":
        show_funnel_audit()
    elif selected == "Corrispettivi":
        show_invoices()

if __name__ == "__main__":
    main()