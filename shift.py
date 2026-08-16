import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import io
import calendar
from datetime import datetime, timedelta

# Configurazione pagina Streamlit
st.set_page_config(page_title="ShiftIA — Gestione Turni", page_icon="🤖", layout="wide")

# ==========================================
# 1. HELPER E UTILITIES
# ==========================================
def safe_int(val):
    """Converte in modo sicuro i valori delle celle in interi."""
    if pd.isna(val) or val is None:
        return 0
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0

TRANSLATIONS = {
    "IT": {
        "tagline": "La pianificazione dei turni per qualsiasi settore aziendale.",
        "badge": "✨ Intelligenza Artificiale per la gestione del personale",
        "intro_desc": "Configura la tua struttura, definisci i fabbisogni e calcola la copertura ideale senza buchi o sovrapposizioni.",
        "role_employee_title": "👤 DIPENDENTE / OPERATORE",
        "role_employee_desc": "Consulta i tuoi turni, gestisci la disponibilità e proponi scambi con i colleghi.",
        "role_employee_btn": "🚀 Entra come Operatore",
        "role_manager_title": "👔 GESTORE / ADMINISTRATOR",
        "role_manager_desc": "Configura reparti, mansioni, orari, gestisci assenze e genera la griglia turni.",
        "role_manager_btn": "🔑 Accesso Gestore",
        "footer_text": "ShiftIA — Workforce & Shift Management System | Developed by Antonio Mercuri",
        "back_btn": "⬅️ Torna Indietro",
    }
}

def init_session_state():
    if "lingua" not in st.session_state:
        st.session_state.lingua = "IT"

    if "show_tips" not in st.session_state:
        st.session_state.show_tips = True

    # Elenco Gestori (Per tablet condivisi)
    if "lista_gestori" not in st.session_state:
        st.session_state.lista_gestori = []

    if "ruolo_accesso" not in st.session_state:
        st.session_state.ruolo_accesso = None

    if "autenticato_gestore" not in st.session_state:
        st.session_state.autenticato_gestore = False

    if "gestore_corrente" not in st.session_state:
        st.session_state.gestore_corrente = None

    if "dipendente_corrente" not in st.session_state:
        st.session_state.dipendente_corrente = None

    if "sezione_gestore" not in st.session_state:
        st.session_state.sezione_gestore = "Dashboard"

    if "mostra_registrazione_gestore" not in st.session_state:
        st.session_state.mostra_registrazione_gestore = False

    if "reparti_custom" not in st.session_state:
        st.session_state.reparti_custom = []

    if "mansioni_custom" not in st.session_state:
        st.session_state.mansioni_custom = []

    if "dipendenti" not in st.session_state:
        st.session_state.dipendenti = []

    if "config_orari_attivita" not in st.session_state:
        st.session_state.config_orari_attivita = {
            "giorni_chiusura": [],
            "turni_definiti": ["Turno Mattina", "Turno Pomeriggio", "Turno Notte"]
        }

    if "fabbisogno_per_reparto" not in st.session_state:
        st.session_state.fabbisogno_per_reparto = {}

    if "registro_assenze" not in st.session_state:
        st.session_state.registro_assenze = []

    if "archivio_turni" not in st.session_state:
        st.session_state.archivio_turni = {}

    if "griglia_corrente" not in st.session_state:
        st.session_state.griglia_corrente = None

    if "chat_messaggi" not in st.session_state:
        st.session_state.chat_messaggi = []

    if "richieste_scambio" not in st.session_state:
        st.session_state.richieste_scambio = []

    # Wizard Interattivo
    if "wizard_attivo" not in st.session_state:
        st.session_state.wizard_attivo = False
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 0

def t(key):
    lang = st.session_state.lingua
    return TRANSLATIONS.get(lang, TRANSLATIONS["IT"]).get(key, "")

def render_tip(testo):
    if st.session_state.show_tips:
        st.info(f"💡 **Tip ShiftIA:** {testo}")

def get_fabbisogno_reparto_df(nome_reparto):
    """Inizializza la griglia fabbisogno con default = 1 persona per turno."""
    if nome_reparto not in st.session_state.fabbisogno_per_reparto:
        turni = st.session_state.config_orari_attivita["turni_definiti"]
        if not turni:
            turni = ["Turno Mattina", "Turno Pomeriggio"]
        
        data = {
            "Turno": turni,
            "Lunedì": [1] * len(turni),
            "Martedì": [1] * len(turni),
            "Mercoledì": [1] * len(turni),
            "Giovedì": [1] * len(turni),
            "Venerdì": [1] * len(turni),
            "Sabato": [1] * len(turni),
            "Domenica": [0] * len(turni)
        }
        st.session_state.fabbisogno_per_reparto[nome_reparto] = pd.DataFrame(data)
    return st.session_state.fabbisogno_per_reparto[nome_reparto]

# ==========================================
# 2. STILI CSS CUSTOM
# ==========================================
def inject_custom_css():
    st.markdown(
        """
        <style>
        .welcome-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            color: #ffffff;
            margin-bottom: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .welcome-title {
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(90deg, #38bdf8, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .user-welcome-box {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border-radius: 16px;
            padding: 20px;
            color: white;
            margin-bottom: 20px;
            border-left: 5px solid #38bdf8;
        }

        .wizard-box {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border: 2px solid #a855f7;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            color: white;
        }

        .calendar-card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px;
            min-height: 100px;
            color: #f8fafc;
            margin-bottom: 10px;
        }

        .calendar-card-today {
            background-color: #0f172a;
            border: 2px solid #38bdf8;
            border-radius: 10px;
            padding: 10px;
            min-height: 100px;
            color: #ffffff;
            margin-bottom: 10px;
        }

        .day-number {
            font-size: 18px;
            font-weight: bold;
            color: #38bdf8;
        }

        .badge-event {
            font-size: 11px;
            padding: 2px 6px;
            border-radius: 4px;
            margin-top: 4px;
            display: block;
        }
        .badge-assenza { background-color: #ef4444; color: white; }
        
        .chat-bubble-me {
            background-color: #0284c7;
            color: white;
            padding: 10px 14px;
            border-radius: 12px 12px 2px 12px;
            margin: 6px 0;
            max-width: 80%;
            margin-left: auto;
        }
        .chat-bubble-other {
            background-color: #334155;
            color: #f8fafc;
            padding: 10px 14px;
            border-radius: 12px 12px 12px 2px;
            margin: 6px 0;
            max-width: 80%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_footer():
    st.markdown(
        f"""
        <br><hr>
        <p style='text-align: center; font-size: 12px; color: #888888;'>
            <b>ShiftIA</b> — {t('footer_text')}
        </p>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# 3. WIZARD INTERATTIVO
# ==========================================
def render_wizard():
    steps = [
        {
            "titolo": "Passo 1: Struttura Aziendale 📊",
            "desc": "Definisci Reparti (es. Cucina, Sala), Mansioni, nomi dei turni e giorni di chiusura.",
            "target": "Tab 1: Struttura Aziendale"
        },
        {
            "titolo": "Passo 2: Staff & Anagrafica 👥",
            "desc": "Censisci i collaboratori con Reparto, Mansioni, Tetto Ore Settimanali e **Giorni di Riposo Spettanti**.",
            "target": "Tab 2: Staff & Anagrafica"
        },
        {
            "titolo": "Passo 3: Fabbisogno Operativo 📈",
            "desc": "Imposta quante persone servono per ciascun turno e giorno della settimana.",
            "target": "Tab 3: Fabbisogno Operativo"
        },
        {
            "titolo": "Passo 4: Registro Assenze 📅",
            "desc": "Registra ferie, permessi o malattia per escludere gli operatori dal calcolo dei turni.",
            "target": "Tab 4: Calendario & Assenze"
        },
        {
            "titolo": "Passo 5: Calcolo IA dei Turni ⚡",
            "desc": "Clicca su **'GENERAZIONE OTTIMIZZATA TURNI'**. L'algoritmo bilancerà ore, riposi e fabbisogno.",
            "target": "Tab 5: Generatore IA"
        },
        {
            "titolo": "Passo 6: Pubblicazione & Portale Dipendenti 🚀",
            "desc": "Revisiona la griglia e pubblicala. Gli operatori potranno consultarla dal loro portale!",
            "target": "Tab 6 & Portale Operatore"
        }
    ]

    curr_step = st.session_state.wizard_step
    
    st.markdown(
        f"""
        <div class="wizard-box">
            <h3 style="margin:0; color:#a855f7;">🧙‍♂️ Guida Interattiva ShiftIA — Step {curr_step + 1} di {len(steps)}</h3>
            <h4 style="margin:8px 0; color:#38bdf8;">{steps[curr_step]['titolo']}</h4>
            <p style="font-size:15px; color:#e2e8f0;">{steps[curr_step]['desc']}</p>
            <p style="font-size:12px; color:#94a3b8;">📍 <b>Sezione:</b> {steps[curr_step]['target']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress((curr_step + 1) / len(steps))

    col_w1, col_w2, col_w3 = st.columns([1, 1, 1])
    with col_w1:
        if curr_step > 0:
            if st.button("⬅️ Precedente", use_container_width=True):
                st.session_state.wizard_step -= 1
                st.rerun()
    with col_w2:
        if st.button("❌ Chiudi Guida", use_container_width=True):
            st.session_state.wizard_attivo = False
            st.rerun()
    with col_w3:
        if curr_step < len(steps) - 1:
            if st.button("Successivo ➡️", type="primary", use_container_width=True):
                st.session_state.wizard_step += 1
                st.rerun()
        else:
            if st.button("🎉 Completa Tour", type="primary", use_container_width=True):
                st.session_state.wizard_attivo = False
                st.session_state.wizard_step = 0
                st.rerun()

# ==========================================
# 4. GENERATORE IMMAGINE TURNI
# ==========================================
def genera_immagine_turni(df):
    width, height = 1200, 110 + (max(len(df), 1) * 55)
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    draw.rectangle([(0, 0), (width, 60)], fill=(15, 23, 42))
    draw.text((20, 20), "SHIFTIA — PROGRAMMAZIONE TURNI OPERATIVI", fill=(255, 255, 255))

    cols = list(df.columns)
    col_width = width // max(len(cols), 1)
    
    for j, col in enumerate(cols):
        draw.rectangle([(j * col_width, 60), ((j + 1) * col_width, 95)], fill=(226, 232, 240), outline=(203, 213, 225))
        draw.text((j * col_width + 8, 72), str(col)[:12], fill=(15, 23, 42))

    for i, row in df.iterrows():
        y_top = 95 + (i * 55)
        for j, col in enumerate(cols):
            val = str(row[col])
            bg_color = (255, 255, 255) if i % 2 == 0 else (248, 250, 252)
            if "RIPOSO" in val:
                bg_color = (254, 226, 226)
            elif "Ferie" in val or "Assenza" in val or "🚫" in val or "Malattia" in val or "Permesso" in val:
                bg_color = (254, 243, 199)
            
            draw.rectangle([(j * col_width, y_top), ((j + 1) * col_width, y_top + 55)], fill=bg_color, outline=(226, 232, 240))
            draw.text((j * col_width + 6, y_top + 10), val[:16], fill=(15, 23, 42))

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()

# ==========================================
# 5. LANDING PAGE
# ==========================================
def schermata_landing():
    top_col1, top_col2 = st.columns([3, 1])
    with top_col2:
        lang_choice = st.selectbox(
            "🌐 Lingua / Language",
            options=["IT 🇮🇹", "EN 🇬🇧", "ES 🇪🇸"],
            index=["IT", "EN", "ES"].index(st.session_state.lingua)
        )
        st.session_state.lingua = lang_choice.split()[0]

    st.markdown(
        f"""
        <div class="welcome-card">
            <div style="font-size:14px; color:#38bdf8; font-weight:bold; margin-bottom:8px;">{t('badge')}</div>
            <div class="welcome-title">🤖 ShiftIA</div>
            <div style="font-size:18px; color:#cbd5e1; margin-bottom:12px;"><b>{t('tagline')}</b></div>
            <p style="font-size: 14px; color: #94a3b8; max-width: 600px; margin: 0 auto;">{t('intro_desc')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {t('role_employee_title')}")
        st.write(t('role_employee_desc'))
        if st.button(t('role_employee_btn'), use_container_width=True, type="primary"):
            st.session_state.ruolo_accesso = "Dipendente"
            st.rerun()

    with col2:
        st.markdown(f"### {t('role_manager_title')}")
        st.write(t('role_manager_desc'))
        if st.button(t('role_manager_btn'), use_container_width=True):
            st.session_state.ruolo_accesso = "Gestore"
            st.rerun()

    render_footer()

# ==========================================
# 6. AUTHENTICATION GESTORE (MULTITABLET / MULTIUTENTE)
# ==========================================
def schermata_auth_gestore():
    if st.button(t('back_btn')):
        st.session_state.ruolo_accesso = None
        st.session_state.mostra_registrazione_gestore = False
        st.rerun()
    
    if not st.session_state.lista_gestori or st.session_state.mostra_registrazione_gestore:
        st.title("📝 Registrazione Nuovo Gestore / Administrator")
        st.info("Crea un account gestore per iniziare ad operare su questo dispositivo.")
        
        with st.form("form_reg_gestore", clear_on_submit=True):
            n_g = st.text_input("Nome")
            c_g = st.text_input("Cognome")
            pwd_g = st.text_input("Password", type="password")
            btn_reg = st.form_submit_button("Crea Account Gestore 🚀", use_container_width=True)

            if btn_reg:
                if n_g.strip() and c_g.strip() and pwd_g.strip():
                    nuovo_g = {
                        "nome": n_g.strip(),
                        "cognome": c_g.strip(),
                        "password": pwd_g.strip()
                    }
                    st.session_state.lista_gestori.append(nuovo_g)
                    st.session_state.gestore_corrente = nuovo_g
                    st.session_state.autenticato_gestore = True
                    st.session_state.sezione_gestore = "Dashboard"
                    st.session_state.mostra_registrazione_gestore = False
                    st.session_state.wizard_attivo = True
                    st.success("✅ Gestore registrato con successo!")
                    st.rerun()
                else:
                    st.warning("⚠️ Compila tutti i campi obbligatori.")
    else:
        st.title("🔑 Accesso Gestore")
        st.info("📱 Dispositivo/Tablet Condiviso: Seleziona il tuo profilo dall'elenco.")
        
        opzioni_gestori = [f"{g['nome']} {g['cognome']}" for g in st.session_state.lista_gestori]
        
        with st.form("form_login_gestore", clear_on_submit=True):
            gestore_scelto_str = st.selectbox("Seleziona il tuo Profilo Gestore:", options=opzioni_gestori)
            pwd_in = st.text_input("Password", type="password")
            rimani_collegato = st.checkbox("📌 Rimani collegato su questo dispositivo", value=True)
            
            btn_log = st.form_submit_button("Entra in ShiftIA 🚀", use_container_width=True)

            if btn_log:
                idx = opzioni_gestori.index(gestore_scelto_str)
                target_g = st.session_state.lista_gestori[idx]
                
                if pwd_in == target_g["password"]:
                    st.session_state.gestore_corrente = target_g
                    st.session_state.autenticato_gestore = True
                    st.session_state.sezione_gestore = "Dashboard"
                    st.success(f"Benvenuto {target_g['nome']}!")
                    st.rerun()
                else:
                    st.error("❌ Password errata.")

        if st.button("➕ Registra un altro Gestore su questo dispositivo", use_container_width=True):
            st.session_state.mostra_registrazione_gestore = True
            st.rerun()

# ==========================================
# 7. AREA GESTORE
# ==========================================
def render_area_gestore():
    top1, top2, top3 = st.columns([3, 1, 1])
    with top2:
        if st.button("🧙‍♂️ Guida & Wizard", use_container_width=True):
            st.session_state.wizard_attivo = not st.session_state.wizard_attivo
            st.session_state.wizard_step = 0
            st.rerun()
    with top3:
        if st.button("🚪 Esci Account", use_container_width=True):
            st.session_state.autenticato_gestore = False
            st.session_state.gestore_corrente = None
            st.rerun()

    dati = st.session_state.gestore_corrente
    st.markdown(
        f"""
        <div class="user-welcome-box">
            <h2 style="margin:0;">Pannello di Controllo — {dati['nome']} {dati['cognome']} 👋</h2>
            <p style="margin:4px 0 0 0; color:#cbd5e1;">Pianificazione turni e gestione della forza lavoro.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.wizard_attivo:
        render_wizard()

    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📊 Struttura Aziendale",
        "👥 Staff & Anagrafica",
        "📈 Fabbisogno Operativo",
        "📅 Calendario & Assenze",
        "⚡ Generatore IA",
        "⚙️ Impostazioni & Archivio"
    ])

    # --- TAB 1: STRUTTURA AZIENDALE ---
    with t1:
        st.subheader("📊 Definizione Reparti, Mansioni e Turni")
        render_tip("Configura i reparti e le mansioni operative della tua struttura.")

        col_r, col_m = st.columns(2)
        with col_r:
            st.markdown("##### 🏢 Reparti / Settori")
            with st.form("form_add_reparto", clear_on_submit=True):
                n_r = st.text_input("Nome Reparto/Area")
                btn_r = st.form_submit_button("➕ Aggiungi Reparto", use_container_width=True)
                if btn_r and n_r.strip():
                    if n_r.strip() not in st.session_state.reparti_custom:
                        st.session_state.reparti_custom.append(n_r.strip())
                        st.success(f"Aggiunto reparto: '{n_r.strip()}'")
                        st.rerun()
            
            if st.session_state.reparti_custom:
                for r in st.session_state.reparti_custom:
                    st.write(f"• **{r}**")
            else:
                st.info("Nessun reparto attualmente configurato.")

        with col_m:
            st.markdown("##### 🛠️ Mansioni / Qualifiche")
            with st.form("form_add_mansione", clear_on_submit=True):
                n_m = st.text_input("Nome Mansione/Ruolo")
                btn_m = st.form_submit_button("➕ Aggiungi Mansione", use_container_width=True)
                if btn_m and n_m.strip():
                    if n_m.strip() not in st.session_state.mansioni_custom:
                        st.session_state.mansioni_custom.append(n_m.strip())
                        st.success(f"Aggiunta mansione: '{n_m.strip()}'")
                        st.rerun()

            if st.session_state.mansioni_custom:
                for m in st.session_state.mansioni_custom:
                    st.write(f"• **{m}**")
            else:
                st.info("Nessuna mansione attualmente configurata.")

        st.markdown("---")
        st.markdown("##### ⏱️ Configurazione Nomi Turni Personalizzati")
        turni_attuali = ", ".join(st.session_state.config_orari_attivita["turni_definiti"])
        nuovi_turni_str = st.text_input(
            "Inserisci i nomi dei turni della tua attività (separati da virgola):", 
            value=turni_attuali
        )
        if st.button("💾 Aggiorna Tipologie Turno", use_container_width=True):
            lista_t = [t.strip() for t in nuovi_turni_str.split(",") if t.strip()]
            st.session_state.config_orari_attivita["turni_definiti"] = lista_t
            st.success("✅ Tipologie di turno aggiornate!")

        st.markdown("---")
        st.markdown("##### 🛑 Giorni di Chiusura Attività")
        giorni_comp = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        chiusure_scelte = st.multiselect(
            "Giorni di chiusura settimanale:",
            options=giorni_comp,
            default=st.session_state.config_orari_attivita["giorni_chiusura"]
        )
        if st.button("💾 Salva Giorni Chiusura", use_container_width=True):
            st.session_state.config_orari_attivita["giorni_chiusura"] = chiusure_scelte
            st.success("✅ Salva configurazione chiusure.")

    # --- TAB 2: STAFF & ANAGRAFICA ---
    with t2:
        st.subheader("👥 Anagrafica Personale & Regole Contrattuali")
        render_tip("Imposta per ogni collaboratore sia le ore massime che i **giorni di riposo spettanti**.")

        if not st.session_state.reparti_custom:
            st.warning("⚠️ Registra almeno un Reparto nella scheda 'Struttura Aziendale' prima di aggiungere personale.")

        with st.expander("➕ Inserisci Nuovo Collaboratore", expanded=True):
            with st.form("form_add_dip", clear_on_submit=True):
                col_n, col_c = st.columns(2)
                with col_n:
                    n = st.text_input("Nome")
                with col_c:
                    c = st.text_input("Cognome")
                
                rep_sel = st.selectbox(
                    "Reparto Principale di Appartenenza", 
                    st.session_state.reparti_custom if st.session_state.reparti_custom else ["Nessun reparto"]
                )
                m_sel = st.multiselect(
                    "Mansioni Abilitate / Competenze", 
                    st.session_state.mansioni_custom if st.session_state.mansioni_custom else ["Nessuna mansione"]
                )
                
                col_o1, col_o2 = st.columns(2)
                with col_o1:
                    ore = st.number_input("Max Ore Settimanali Contrattuali", value=40, step=1)
                with col_o2:
                    riposi = st.number_input("Giorni di Riposo Spettanti (Settimanali)", value=2, min_value=0, max_value=6, step=1)

                if st.form_submit_button("💾 Registra Collaboratore", use_container_width=True):
                    if n.strip() and c.strip() and st.session_state.reparti_custom:
                        st.session_state.dipendenti.append({
                            "ID": len(st.session_state.dipendenti) + 1,
                            "Nome": n.strip(), "Cognome": c.strip(),
                            "Reparto": rep_sel, "Mansioni": m_sel, 
                            "Max_Ore": ore, "Giorni_Riposo": riposi
                        })
                        st.success(f"✅ Registrato: {n} {c}")
                        st.rerun()
                    else:
                        st.error("Inserisci Nome, Cognome e assicurati di aver creato almeno un reparto.")

        st.markdown("#### Lista Personale Inserito")
        if st.session_state.dipendenti:
            st.dataframe(pd.DataFrame(st.session_state.dipendenti), use_container_width=True)

            st.markdown("---")
            st.markdown("##### 🗑️ Rimuovi Collaboratore")
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                opzioni_dip = [f"ID #{d['ID']}: {d['Nome']} {d['Cognome']} ({d['Reparto']})" for d in st.session_state.dipendenti]
                dip_scelto_del = st.selectbox("Seleziona collaboratore da eliminare:", options=opzioni_dip, key="select_del_dip")
            with col_del2:
                st.write("")
                st.write("")
                if st.button("🗑️ Rimuovi", type="primary", use_container_width=True, key="btn_del_dip"):
                    idx_del = opzioni_dip.index(dip_scelto_del)
                    rimosso = st.session_state.dipendenti.pop(idx_del)
                    st.success(f"✅ **{rimosso['Nome']} {rimosso['Cognome']}** eliminato!")
                    st.rerun()
        else:
            st.info("Nessun membro del personale inserito.")

    # --- TAB 3: FABBISOGNO OPERATIVO ---
    with t3:
        st.subheader("📈 Fabbisogno del Personale per Reparto")
        render_tip("Imposta quante persone servono per ogni specifico turno nei giorni della settimana.")
        
        if not st.session_state.reparti_custom:
            st.warning("⚠️ Registra i reparti nella prima scheda per poter compilare la griglia dei fabbisogni.")
        else:
            rep_selezionato = st.selectbox(
                "📍 Seleziona il Reparto/Area da configurare:",
                options=st.session_state.reparti_custom,
                key="select_reparto_fabbisogno"
            )

            if rep_selezionato:
                st.markdown(f"##### Griglia Copertura Richiesta per: **{rep_selezionato}**")
                df_reparto = get_fabbisogno_reparto_df(rep_selezionato)

                df_fab_edit = st.data_editor(
                    df_reparto,
                    use_container_width=True,
                    num_rows="dynamic",
                    key=f"editor_fabbisogno_{rep_selezionato}"
                )
                st.session_state.fabbisogno_per_reparto[rep_selezionato] = df_fab_edit

    # --- TAB 4: CALENDARIO & ASSENZE ---
    with t4:
        st.subheader("📅 Registro Assenze & Disponibilità")
        render_tip("Registra ferie o permessi. L'algoritmo li escluderà dal calcolo turni.")

        oggi = datetime.now()
        cal = calendar.monthcalendar(oggi.year, oggi.month)
        giorni_settimana = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
        
        cols_header = st.columns(7)
        for idx, h in enumerate(giorni_settimana):
            cols_header[idx].markdown(f"<p style='text-align:center; font-weight:bold; color:#38bdf8;'>{h}</p>", unsafe_allow_html=True)

        for week in cal:
            cols_week = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    data_curr = datetime(oggi.year, oggi.month, day).date()
                    is_today = (day == oggi.day)
                    card_class = "calendar-card-today" if is_today else "calendar-card"
                    
                    html_content = f"<div class='{card_class}'><div class='day-number'>{day}</div>"
                    for ass in st.session_state.registro_assenze:
                        d_i = datetime.strptime(ass["Inizio"], "%Y-%m-%d").date()
                        d_f = datetime.strptime(ass["Fine"], "%Y-%m-%d").date()
                        if d_i <= data_curr <= d_f:
                            html_content += f"<span class='badge-event badge-assenza'>🚫 {ass['Dipendente'].split()[0]}: {ass['Tipo']}</span>"
                    html_content += "</div>"
                    cols_week[i].markdown(html_content, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("➕ Nuova Segnalazione Assenza / Permesso")
        if st.session_state.dipendenti:
            with st.form("form_assenza", clear_on_submit=True):
                dip_scelto = st.selectbox("Seleziona Persona:", [f"{d['Nome']} {d['Cognome']}" for d in st.session_state.dipendenti])
                tipo_assenza = st.selectbox("Motivazione Assenza:", ["Ferie", "Permesso", "Malattia", "Formazione"])
                data_inizio = st.date_input("Inizio:", datetime.now())
                data_fine = st.date_input("Fine:", datetime.now())

                if st.form_submit_button("💾 Salva Assenza", use_container_width=True):
                    st.session_state.registro_assenze.append({
                        "Dipendente": dip_scelto,
                        "Inizio": str(data_inizio),
                        "Fine": str(data_fine),
                        "Tipo": tipo_assenza
                    })
                    st.success(f"✅ Assenza salvata per {dip_scelto}!")
                    st.rerun()
        else:
            st.info("Nessun dipendente a cui assegnare un'assenza.")

    # --- TAB 5: GENERATORE IA POTENZIATO ---
    with t5:
        st.subheader("⚡ Algoritmo Generatore Turni Intelligente")
        render_tip("L'algoritmo calcola i turni incrociando: **Fabbisogno Reparto, Ore Max, Giorni di Riposo Spettanti, Assenze e Giorni di Chiusura**.")

        data_riferimento = st.date_input("Seleziona data di inizio settimana:", datetime.now() + timedelta(days=7))
        lunedi_scelto = data_riferimento - timedelta(days=data_riferimento.weekday())

        if st.button("🤖 GENERAZIONE OTTIMIZZATA TURNI", type="primary", use_container_width=True):
            if not st.session_state.dipendenti:
                st.warning("⚠️ Nessun collaboratore censito nello Staff.")
            elif not st.session_state.reparti_custom:
                st.warning("⚠️ Nessun reparto configurato.")
            else:
                giorni_settimana = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
                chiusure = st.session_state.config_orari_attivita["giorni_chiusura"]
                date_settimana = [lunedi_scelto + timedelta(days=i) for i in range(7)]

                ore_accumulate = {f"{d['Nome']} {d['Cognome']}": 0 for d in st.session_state.dipendenti}
                riposi_effettuati = {f"{d['Nome']} {d['Cognome']}": 0 for d in st.session_state.dipendenti}

                matrice_turni = {
                    f"{d['Nome']} {d['Cognome']}": {
                        "Reparto": d.get("Reparto", "Generale"),
                        "Max_Ore": d.get("Max_Ore", 40),
                        "Giorni_Riposo": d.get("Giorni_Riposo", 2)
                    } for d in st.session_state.dipendenti
                }

                # Step 1: Pre-compilazione Chiusure, Assenze e Inizializzazione
                for idx, g in enumerate(giorni_settimana):
                    data_curr = date_settimana[idx]
                    for dip in st.session_state.dipendenti:
                        nome_c = f"{dip['Nome']} {dip['Cognome']}"

                        if g in chiusure:
                            matrice_turni[nome_c][g] = "CHIUSURA"
                            continue

                        assenza_trovata = None
                        for ass in st.session_state.registro_assenze:
                            if ass["Dipendente"] == nome_c:
                                d_i = datetime.strptime(ass["Inizio"], "%Y-%m-%d").date()
                                d_f = datetime.strptime(ass["Fine"], "%Y-%m-%d").date()
                                if d_i <= data_curr <= d_f:
                                    assenza_trovata = ass["Tipo"]
                                    break

                        if assenza_trovata:
                            matrice_turni[nome_c][g] = f"🚫 {assenza_trovata}"
                        else:
                            matrice_turni[nome_c][g] = "LIBERO"

                # Step 2: Assegnazione Turni per Copertura Fabbisogno
                for idx, g in enumerate(giorni_settimana):
                    if g in chiusure:
                        continue

                    for rep_nome in st.session_state.reparti_custom:
                        df_fab = get_fabbisogno_reparto_df(rep_nome)

                        for _, row_fab in df_fab.iterrows():
                            nome_turno = str(row_fab["Turno"])
                            persone_richieste = safe_int(row_fab.get(g, 0))
                            ore_turno = 8
                            persone_assegnate = 0

                            # Candidati del reparto disponibile
                            dip_candidati = [
                                d for d in st.session_state.dipendenti 
                                if str(d.get("Reparto")).strip().lower() == str(rep_nome).strip().lower()
                            ]

                            # Ordina per chi ha lavorato meno ore per bilanciare il carico
                            dip_candidati = sorted(
                                dip_candidati, 
                                key=lambda x: ore_accumulate[f"{x['Nome']} {x['Cognome']}"]
                            )

                            for d in dip_candidati:
                                nome_c = f"{d['Nome']} {d['Cognome']}"
                                max_o = d.get("Max_Ore", 40)
                                ore_attuali = ore_accumulate[nome_c]

                                if matrice_turni[nome_c][g] == "LIBERO" and (ore_attuali + ore_turno <= max_o):
                                    if persone_assegnate < persone_richieste:
                                        matrice_turni[nome_c][g] = nome_turno
                                        ore_accumulate[nome_c] += ore_turno
                                        persone_assegnate += 1

                # Step 3: Formalizzazione Riposi Spettanti
                for dip in st.session_state.dipendenti:
                    nome_c = f"{dip['Nome']} {dip['Cognome']}"
                    riposi_dovuti = dip.get("Giorni_Riposo", 2)
                    
                    for g in giorni_settimana:
                        if matrice_turni[nome_c][g] == "LIBERO":
                            if riposi_effettuati[nome_c] < riposi_dovuti:
                                matrice_turni[nome_c][g] = "RIPOSO"
                                riposi_effettuati[nome_c] += 1
                            else:
                                matrice_turni[nome_c][g] = "DISPONIBILE"

                # Costruzione DataFrame finale
                lista_righe = []
                for nome_c, val in matrice_turni.items():
                    riga = {
                        "Operatore": nome_c, 
                        "Reparto": val["Reparto"], 
                        "Totale Ore": f"{ore_accumulate[nome_c]}h / {val['Max_Ore']}h",
                        "Riposi": f"{riposi_effettuati[nome_c]} / {val['Giorni_Riposo']}"
                    }
                    for g in giorni_settimana:
                        riga[g] = val.get(g, "RIPOSO")
                    lista_righe.append(riga)

                st.session_state.griglia_corrente = pd.DataFrame(lista_righe)
                st.success("✅ Generazione Turni completata con successo!")

        if st.session_state.griglia_corrente is not None:
            st.markdown("#### ✏️ Modifica e Pubblicazione della Griglia")
            df_edit = st.data_editor(st.session_state.griglia_corrente, use_container_width=True)
            
            if st.button("🔒 PUBBLICA PIANIFICAZIONE PER IL PERSONALE", type="primary", use_container_width=True):
                k = f"Settimana_{lunedi_scelto.strftime('%d_%m_%Y')}"
                st.session_state.archivio_turni[k] = {
                    "settimana": lunedi_scelto.strftime('%d/%m/%Y'),
                    "dataframe": df_edit
                }
                st.success("✅ Pianificazione pubblicata e visibile agli operatori!")

    # --- TAB 6: ARCHIVIO & IMPOSTAZIONI ---
    with t6:
        st.subheader("⚙️ Impostazioni e Storico Pianificazioni")
        st.session_state.show_tips = st.toggle("Mostra Suggerimenti/Tip di sistema", value=st.session_state.show_tips)
        
        st.markdown("---")
        st.markdown("#### 📁 Archivio Turni Pubblicati")
        if not st.session_state.archivio_turni:
            st.info("Nessuna pianificazione pubblicata finora.")
        else:
            for chiave, dati_arc in st.session_state.archivio_turni.items():
                with st.expander(f"📌 Programmazione Settimana del {dati_arc['settimana']}"):
                    df_arc = dati_arc["dataframe"]
                    st.dataframe(df_arc, use_container_width=True)
                    img_bytes = genera_immagine_turni(df_arc)
                    st.download_button(
                        label="📥 Scarica Tabella in Immagine (PNG)",
                        data=img_bytes,
                        file_name=f"Turni_{dati_arc['settimana'].replace('/', '_')}.png",
                        mime="image/png",
                        key=f"dl_manager_{chiave}",
                        use_container_width=True
                    )

# ==========================================
# 8. AREA DIPENDENTE / OPERATORE
# ==========================================
def render_area_dipendente():
    top1, top2 = st.columns([4, 1])
    with top2:
        if st.button("🚪 Esci Profilo", use_container_width=True):
            st.session_state.ruolo_accesso = None
            st.session_state.dipendente_corrente = None
            st.rerun()

    if st.session_state.dipendente_corrente is None:
        st.title("👤 Portale Operatore")
        if not st.session_state.dipendenti:
            st.warning("⚠️ Nessun operatore censito nel sistema. Richiedi al gestore di inserirti in anagrafica.")
            return

        lista_dip_nomi = [f"{d['Nome']} {d['Cognome']} — [{d.get('Reparto', 'Generale')}]" for d in st.session_state.dipendenti]
        
        with st.form("form_login_dip", clear_on_submit=False):
            scelta = st.selectbox("Seleziona il tuo Profilo:", options=lista_dip_nomi)
            rimani_collegato_dip = st.checkbox("📌 Rimani collegato", value=True)
            btn_ent = st.form_submit_button("🚀 Entra nel Portale", use_container_width=True)

            if btn_ent:
                idx_scelto = lista_dip_nomi.index(scelta)
                st.session_state.dipendente_corrente = st.session_state.dipendenti[idx_scelto]
                st.rerun()
    else:
        dip = st.session_state.dipendente_corrente
        st.markdown(
            f"""
            <div class="user-welcome-box">
                <h3 style="margin:0;">Benvenuto/a, {dip['Nome']} {dip['Cognome']} 👋</h3>
                <p style="margin:2px 0 0 0; color:#cbd5e1;">Reparto: <b>{dip.get('Reparto')}</b> | Max Ore: <b>{dip.get('Max_Ore')}h</b> | Riposi Spettanti: <b>{dip.get('Giorni_Riposo')} gg</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_d1, tab_d2, tab_d3 = st.tabs(["📅 I Miei Turni", "🔄 Proponi Scambio", "💬 Comunicazioni Team"])

        with tab_d1:
            st.subheader("📅 Turnazione Pubblicata")
            if not st.session_state.archivio_turni:
                st.info("ℹ️ Nessuna tabella turni pubblicata.")
            else:
                for k, dati_t in st.session_state.archivio_turni.items():
                    st.markdown(f"**Programmazione dal {dati_t['settimana']}**")
                    st.dataframe(dati_t["dataframe"], use_container_width=True)

        with tab_d2:
            st.subheader("🔄 Modulo Richiesta Scambio Turno")
            colleghi = [f"{d['Nome']} {d['Cognome']}" for d in st.session_state.dipendenti if d['ID'] != dip['ID']]
            if not colleghi:
                st.warning("Nessun collega disponibile.")
            else:
                with st.form("form_scambio", clear_on_submit=True):
                    sostituto = st.selectbox("Seleziona Collega Proposto:", colleghi)
                    giorno = st.selectbox("Giorno del Turno:", ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"])
                    motivo = st.text_area("Note / Motivazione:")
                    if st.form_submit_button("Invia Richiesta 🚀", use_container_width=True):
                        st.session_state.richieste_scambio.append({
                            "Richiedente": f"{dip['Nome']} {dip['Cognome']}",
                            "Giorno_Richiedente": giorno,
                            "Sostituto": sostituto,
                            "Motivazione": motivo,
                            "Stato": "In Attesa"
                        })
                        st.success("✅ Richiesta inviata al gestore!")
                        st.rerun()

        with tab_d3:
            st.subheader("💬 Chat Interna")
            for msg in st.session_state.chat_messaggi:
                is_me = msg["mittente"].startswith(f"{dip['Nome']} {dip['Cognome']}")
                bubble_class = "chat-bubble-me" if is_me else "chat-bubble-other"
                st.markdown(
                    f"""
                    <div class="{bubble_class}">
                        <div style="font-size: 10px; opacity: 0.8;"><b>{msg['mittente']}</b> — {msg['data']}</div>
                        <div>{msg['testo']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with st.form("form_chat", clear_on_submit=True):
                nuovo_msg = st.text_input("Messaggio...")
                if st.form_submit_button("Invia 📤", use_container_width=True) and nuovo_msg.strip():
                    st.session_state.chat_messaggi.append({
                        "mittente": f"{dip['Nome']} {dip['Cognome']}",
                        "testo": nuovo_msg.strip(),
                        "data": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()

# ==========================================
# 9. ROUTER PRINCIPALE
# ==========================================
def main():
    inject_custom_css()
    init_session_state()

    if st.session_state.ruolo_accesso is None:
        schermata_landing()
    elif st.session_state.ruolo_accesso == "Gestore":
        if not st.session_state.autenticato_gestore or st.session_state.gestore_corrente is None:
            schermata_auth_gestore()
        else:
            render_area_gestore()
            render_footer()
    elif st.session_state.ruolo_accesso == "Dipendente":
        render_area_dipendente()
        render_footer()

if __name__ == "__main__":
    main()
