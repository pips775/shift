import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

# Configurazione pagina Streamlit
st.set_page_config(page_title="ShiftIA — Gestione Turni Multi-Azienda", page_icon="🤖", layout="wide")

DB_FILE = "shiftia_db.json"

# ==========================================
# 1. DIZIONARIO TRADUZIONI MULTILINGUA
# ==========================================
TRANSLATIONS = {
    "IT": {
        "tagline": "La pianificazione dei turni per qualsiasi settore aziendale.",
        "badge": "✨ Intelligenza Artificiale per la gestione del personale",
        "intro_desc": "Crea o seleziona la tua Azienda / Workspace simulato per pianificare i turni in totale autonomia senza interferenze.",
        "role_employee_title": "👤 DIPENDENTE / OPERATORE",
        "role_employee_desc": "Consulta i tuoi turni, gestisci la disponibilità e proponi scambi con i colleghi.",
        "role_employee_btn": "🚀 Entra come Operatore",
        "role_manager_title": "👔 GESTORE / ADMINISTRATOR",
        "role_manager_desc": "Configura reparti, mansioni, orari, gestisci assenze e genera la griglia turni.",
        "role_manager_btn": "🔑 Accesso Gestore",
        "footer_text": "ShiftIA — Workforce & Shift Management System | Developed by Antonio Mercuri",
        "back_btn": "⬅️ Torna Indietro",
        "tab_struttura": "📊 Struttura Aziendale",
        "tab_staff": "👥 Staff & Anagrafica",
        "tab_fabbisogno": "📈 Fabbisogno Operativo",
        "tab_assenze": "📅 Calendario & Assenze",
        "tab_generatore": "⚡ Generatore IA",
        "tab_impostazioni": "⚙️ Impostazioni & Archivio",
        "logout_btn": "🚪 Esci / Cambia Azienda",
        "panel_title": "Pannello di Controllo",
        "reparti_title": "🏢 Reparti / Settori",
        "mansioni_title": "🛠️ Mansioni / Qualifiche",
        "add_reparto": "➕ Aggiungi Reparto",
        "add_mansione": "➕ Aggiungi Mansione",
        "delete_btn": "🗑️ Rimuovi",
        "login_gestore_title": "🔑 Accesso Gestore",
        "reg_gestore_title": "📝 Registrazione Nuovo Gestore / Azienda",
        "pass_label": "Password",
        "name_label": "Nome Gestore",
        "surname_label": "Cognome Gestore",
        "company_label": "Nome Azienda / Workspace",
        "login_btn": "Entra in ShiftIA 🚀",
        "reg_btn": "Crea Azienda e Account Gestore 🚀",
        "generate_btn": "🤖 GENERAZIONE OTTIMIZZATA TURNI",
        "publish_btn": "🔒 PUBBLICA PIANIFICAZIONE PER IL PERSONALE",
        "tip_struttura": "Configura i reparti e le mansioni operative della tua struttura.",
        "tip_staff": "Puoi modificare i dati e aggiungere più mansioni direttamente nella tabella qui sotto.",
        "tip_fabbisogno": "Imposta quante persone servono per ogni specifico turno nei giorni della settimana.",
        "tip_assenze": "Registra ferie o permessi. L'algoritmo li escluderà dal calcolo turni.",
        "tip_generatore": "L'algoritmo calcola i turni incrociando: Fabbisogno Reparto, Ore Max, Giorni di Riposo Spettanti e Assenze."
    },
    "EN": {
        "tagline": "Shift planning for any business sector.",
        "badge": "✨ Artificial Intelligence for workforce management",
        "intro_desc": "Create or select your simulated Company / Workspace to schedule shifts independently without interference.",
        "role_employee_title": "👤 EMPLOYEE / OPERATOR",
        "role_employee_desc": "View your shifts, manage availability, and propose shift swaps with colleagues.",
        "role_employee_btn": "🚀 Enter as Operator",
        "role_manager_title": "👔 MANAGER / ADMINISTRATOR",
        "role_manager_desc": "Configure departments, tasks, hours, manage leave, and generate the shift grid.",
        "role_manager_btn": "🔑 Manager Access",
        "footer_text": "ShiftIA — Workforce & Shift Management System | Developed by Antonio Mercuri",
        "back_btn": "⬅️ Back",
        "tab_struttura": "📊 Company Structure",
        "tab_staff": "👥 Staff & Records",
        "tab_fabbisogno": "📈 Operational Needs",
        "tab_assenze": "📅 Calendar & Absence",
        "tab_generatore": "⚡ AI Generator",
        "tab_impostazioni": "⚙️ Settings & Archive",
        "logout_btn": "🚪 Switch Company / Logout",
        "panel_title": "Control Panel",
        "reparti_title": "🏢 Departments / Sectors",
        "mansioni_title": "🛠️ Roles / Tasks",
        "add_reparto": "➕ Add Department",
        "add_mansione": "➕ Add Role",
        "delete_btn": "🗑️ Remove",
        "login_gestore_title": "🔑 Manager Login",
        "reg_gestore_title": "📝 Register New Manager / Company",
        "pass_label": "Password",
        "name_label": "Manager First Name",
        "surname_label": "Manager Last Name",
        "company_label": "Company / Workspace Name",
        "login_btn": "Enter ShiftIA 🚀",
        "reg_btn": "Create Company & Manager Account 🚀",
        "generate_btn": "🤖 OPTIMIZED SHIFT GENERATION",
        "publish_btn": "🔒 PUBLISH SCHEDULE TO STAFF",
        "tip_struttura": "Configure departments and operational tasks for your organization.",
        "tip_staff": "You can edit staff info and assign multiple roles directly inside the table below.",
        "tip_fabbisogno": "Define how many staff members are required for each specific shift across days of the week.",
        "tip_assenze": "Register leave or time-off. The algorithm will exclude them from shift assignment.",
        "tip_generatore": "The algorithm calculates shifts by cross-referencing: Department Needs, Max Hours, Rest Days, and Absences."
    },
    "ES": {
        "tagline": "Planificación de turnos para cualquier sector empresarial.",
        "badge": "✨ Inteligencia Artificial para la gestión del personal",
        "intro_desc": "Crea o selecciona tu Empresa / Espacio simulado para planificar turnos de forma independiente.",
        "role_employee_title": "👤 EMPLEADO / OPERARIO",
        "role_employee_desc": "Consulta tus turnos, gestiona disponibilidad y propone intercambios con compañeros.",
        "role_employee_btn": "🚀 Entrar como Operario",
        "role_manager_title": "👔 GESTOR / ADMINISTRADOR",
        "role_manager_desc": "Configura departamentos, tareas, horarios, gestiona ausencias y genera la cuadrícula.",
        "role_manager_btn": "🔑 Acceso Gestor",
        "footer_text": "ShiftIA — Workforce & Shift Management System | Developed by Antonio Mercuri",
        "back_btn": "⬅️ Volver",
        "tab_struttura": "📊 Estructura Empresa",
        "tab_staff": "👥 Personal y Datos",
        "tab_fabbisogno": "📈 Necesidad Operativa",
        "tab_assenze": "📅 Calendario y Ausencias",
        "tab_generatore": "⚡ Generador IA",
        "tab_impostazioni": "⚙️ Ajustes y Archivo",
        "logout_btn": "🚪 Salir / Cambiar Empresa",
        "panel_title": "Panel de Control",
        "reparti_title": "🏢 Departamentos / Áreas",
        "mansioni_title": "🛠️ Funciones / Puestos",
        "add_reparto": "➕ Añadir Departamento",
        "add_mansione": "➕ Añadir Función",
        "delete_btn": "🗑️ Eliminar",
        "login_gestore_title": "🔑 Acceso Gestor",
        "reg_gestore_title": "📝 Registro Nuevo Gestor / Empresa",
        "pass_label": "Contraseña",
        "name_label": "Nombre del Gestor",
        "surname_label": "Apellido del Gestor",
        "company_label": "Nombre de la Empresa",
        "login_btn": "Entrar en ShiftIA 🚀",
        "reg_btn": "Crear Empresa y Cuenta 🚀",
        "generate_btn": "🤖 GENERACIÓN OPTIMIZADA TURNOS",
        "publish_btn": "🔒 PUBLICAR PROGRAMACIÓN AL PERSONAL",
        "tip_struttura": "Configura los departamentos y funciones operativas de tu empresa.",
        "tip_staff": "Puedes editar la información y asignar múltiples funciones directamente en la tabla.",
        "tip_fabbisogno": "Define cuántas personas se necesitan para cada turno específico en los días de la semana.",
        "tip_assenze": "Registra vacaciones o permisos. El algoritmo los excluirá de la programación.",
        "tip_generatore": "El algoritmo calcula los turnos cruzando: Necesidad por Departamento, Horas Máximas, Días de Descanso y Ausencias."
    }
}

def t(key):
    lang = st.session_state.get("lingua", "IT")
    return TRANSLATIONS.get(lang, TRANSLATIONS["IT"]).get(key, key)

# ==========================================
# 2. PERSISTENZA DATI LOCALE MULTI-AZIENDA
# ==========================================
def salva_dati_locali():
    az = st.session_state.get("azienda_corrente")
    if az and "aziende" in st.session_state and az in st.session_state.aziende:
        fabbisogno_json = {}
        for k, v in st.session_state.fabbisogno_per_reparto.items():
            if isinstance(v, pd.DataFrame):
                fabbisogno_json[k] = v.to_dict(orient="records")
            else:
                fabbisogno_json[k] = v

        archivio_json = {}
        for k, v in st.session_state.archivio_turni.items():
            archivio_json[k] = {
                "settimana": v["settimana"],
                "dataframe": v["dataframe"].to_dict(orient="records") if isinstance(v["dataframe"], pd.DataFrame) else v["dataframe"]
            }

        st.session_state.aziende[az] = {
            "lista_gestori": st.session_state.lista_gestori,
            "reparti_custom": st.session_state.reparti_custom,
            "mansioni_custom": st.session_state.mansioni_custom,
            "dipendenti": st.session_state.dipendenti,
            "config_orari_attivita": st.session_state.config_orari_attivita,
            "fabbisogno_per_reparto": fabbisogno_json,
            "registro_assenze": st.session_state.registro_assenze,
            "archivio_turni": archivio_json,
            "chat_messaggi": st.session_state.chat_messaggi,
            "richieste_scambio": st.session_state.richieste_scambio,
            "wizard_completato": st.session_state.get("wizard_completato", False)
        }

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.get("aziende", {}), f, ensure_ascii=False, indent=4)

def carica_dati_locali():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                dati_aziende = json.load(f)
                st.session_state.aziende = dati_aziende
        except Exception:
            st.session_state.aziende = {}
    else:
        st.session_state.aziende = {}

def imposta_azienda_attiva(az_selezionata_login):
    if not az_selezionata_login:
        st.session_state.azienda_corrente = None
        st.session_state.lista_gestori = []
        return

    dati_az = st.session_state.aziende.get(az_selezionata_login, {})
    st.session_state.azienda_corrente = az_selezionata_login
    st.session_state.lista_gestori = dati_az.get("lista_gestori", [])
    st.session_state.reparti_custom = dati_az.get("reparti_custom", ["Cucina", "Sala", "Bar"])
    st.session_state.mansioni_custom = dati_az.get("mansioni_custom", ["Chef", "Cameriere", "Barista"])
    
    default_dipendenti = [
        {"Nome": "Mario", "Cognome": "Rossi", "Reparto": "Cucina", "Mansione": "Chef", "Ore Max": 40, "Giorni di Riposo": 2},
        {"Nome": "Luca", "Cognome": "Bianchi", "Reparto": "Sala", "Mansione": "Cameriere", "Ore Max": 36, "Giorni di Riposo": 2},
        {"Nome": "Giulia", "Cognome": "Verdi", "Reparto": "Bar", "Mansione": "Barista", "Ore Max": 40, "Giorni di Riposo": 2}
    ]
    st.session_state.dipendenti = dati_az.get("dipendenti", default_dipendenti)
    
    st.session_state.config_orari_attivita = dati_az.get("config_orari_attivita", {
        "giorni_chiusura": [],
        "turni_definiti": ["Turno Mattina", "Turno Pomeriggio", "Turno Notte"]
    })
    
    fabb_raw = dati_az.get("fabbisogno_per_reparto", {})
    fabb_df = {}
    turni = st.session_state.config_orari_attivita["turni_definiti"]
    for rep in st.session_state.reparti_custom:
        if rep in fabb_raw:
            v = fabb_raw[rep]
            fabb_df[rep] = pd.DataFrame(v) if isinstance(v, list) else v
        else:
            fabb_df[rep] = pd.DataFrame({
                "Turno": turni,
                "Lunedì": [1]*len(turni), "Martedì": [1]*len(turni), "Mercoledì": [1]*len(turni),
                "Giovedì": [1]*len(turni), "Venerdì": [1]*len(turni), "Sabato": [1]*len(turni), "Domenica": [0]*len(turni)
            })
    st.session_state.fabbisogno_per_reparto = fabb_df

    st.session_state.registro_assenze = dati_az.get("registro_assenze", [])
    
    arch_raw = dati_az.get("archivio_turni", {})
    arch_df = {}
    for k, v in arch_raw.items():
        df_val = pd.DataFrame(v["dataframe"]) if isinstance(v.get("dataframe"), list) else v.get("dataframe")
        arch_df[k] = {"settimana": v.get("settimana"), "dataframe": df_val}
    st.session_state.archivio_turni = arch_df

    st.session_state.chat_messaggi = dati_az.get("chat_messaggi", [])
    st.session_state.richieste_scambio = dati_az.get("richieste_scambio", [])
    st.session_state.wizard_completato = dati_az.get("wizard_completato", True)

def elimina_azienda(nome_azienda):
    if "aziende" in st.session_state and nome_azienda in st.session_state.aziende:
        del st.session_state.aziende[nome_azienda]
        if st.session_state.get("azienda_corrente") == nome_azienda:
            st.session_state.azienda_corrente = None
            st.session_state.lista_gestori = []
            st.session_state.autenticato_gestore = False
            st.session_state.ruolo_accesso = None
        salva_dati_locali()

# ==========================================
# 3. FUNZIONE SUPPORTO FABBISOGNO (RIPRISTINATA)
# ==========================================
def get_fabbisogno_reparto_df(nome_reparto):
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
# 4. INIZIALIZZAZIONE SESSION STATE
# ==========================================
def init_session_state():
    if "lingua" not in st.session_state:
        st.session_state.lingua = "IT"
    if "show_tips" not in st.session_state:
        st.session_state.show_tips = True
    if "aziende" not in st.session_state:
        st.session_state.aziende = {}
    if "azienda_corrente" not in st.session_state:
        st.session_state.azienda_corrente = None
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
    if "reparti_custom" not in st.session_state:
        st.session_state.reparti_custom = ["Cucina", "Sala", "Bar"]
    if "mansioni_custom" not in st.session_state:
        st.session_state.mansioni_custom = ["Chef", "Cameriere", "Barista"]
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
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
    if "wizard_completato" not in st.session_state:
        st.session_state.wizard_completato = False
    if "dati_caricati_da_file" not in st.session_state:
        carica_dati_locali()
        st.session_state.dati_caricati_da_file = True

def render_tip(key_tip):
    if st.session_state.show_tips:
        st.info(f"💡 **Tip ShiftIA:** {t(key_tip)}")

# ==========================================
# 5. STILI CSS CUSTOM
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
# 6. SCHERMATE PRINCIPALI
# ==========================================
def schermata_landing():
    top_col1, top_col2 = st.columns([3, 1])
    with top_col2:
        col_it, col_en, col_es = st.columns(3)
        with col_it:
            if st.button("🇮🇹", help="Italiano"):
                st.session_state.lingua = "IT"
                st.rerun()
        with col_en:
            if st.button("🇬🇧", help="English"):
                st.session_state.lingua = "EN"
                st.rerun()
        with col_es:
            if st.button("🇪🇸", help="Español"):
                st.session_state.lingua = "ES"
                st.rerun()

    st.markdown(
        f"""
        <div class="welcome-card">
            <div style="font-size:14px; color:#38bdf8; font-weight:bold; margin-bottom:8px;">{t('badge')}</div>
            <div class="welcome-title">🤖 ShiftIA</div>
            <div style="font-size:18px; color:#cbd5e1; margin-bottom:12px;"><b>{t('tagline')}</b></div>
            <p style="font-size: 14px; color: #94a3b8; max-width: 650px; margin: 0 auto;">{t('intro_desc')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🏢 Seleziona o Crea la tua Azienda Simulata")
    elenco_aziende = list(st.session_state.aziende.keys())

    if elenco_aziende:
        col_az_sel, col_az_del = st.columns([4, 1])
        with col_az_sel:
            az_scelta = st.selectbox("📍 Azienda / Workspace Esistente:", options=elenco_aziende)
        with col_az_del:
            st.write("")
            st.write("")
            if st.button("🗑️ Elimina", help=f"Elimina definitivamente l'azienda '{az_scelta}'"):
                elimina_azienda(az_scelta)
                st.success(f"Azienda '{az_scelta}' eliminata!")
                st.rerun()

        if st.button("👉 Seleziona questa Azienda", type="secondary", use_container_width=True):
            imposta_azienda_attiva(az_scelta)
            st.success(f"Azienda attiva impostata su: **{az_scelta}**")
            st.rerun()
    else:
        st.info("ℹ️ Nessuna azienda creata. Inizia creandone una nuova!")

    st.markdown("---")

    if st.session_state.azienda_corrente:
        st.success(f"🏢 **Azienda Attiva:** {st.session_state.azienda_corrente}")
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
    else:
        st.warning("⚠️ Seleziona un'azienda o registrine una nuova qui sotto.")
        if st.button("🔑 Vai alla Registrazione Nuova Azienda / Accesso Gestore", type="primary", use_container_width=True):
            st.session_state.ruolo_accesso = "Gestore"
            st.rerun()

    render_footer()

def schermata_login_gestore():
    st.subheader(t('login_gestore_title'))
    
    if st.button(t('back_btn')):
        st.session_state.ruolo_accesso = None
        st.rerun()

    elenco_aziende = list(st.session_state.aziende.keys())
    
    tab_login, tab_reg = st.tabs(["🔑 Accedi", "📝 Registra Nuova Azienda"])
    
    with tab_login:
        if not elenco_aziende:
            st.warning("Nessuna azienda registrata. Crea la prima azienda nella scheda 'Registra Nuova Azienda'.")
        else:
            az_login = st.selectbox("Seleziona Azienda:", options=elenco_aziende, key="login_az_sel")
            pass_input = st.text_input(t('pass_label'), type="password", key="login_pass")
            
            if st.button(t('login_btn'), type="primary"):
                imposta_azienda_attiva(az_login)
                st.session_state.autenticato_gestore = True
                st.session_state.gestore_corrente = {"nome": "Admin", "cognome": "Gestore"}
                st.success("Accesso effettuato con successo!")
                st.rerun()

    with tab_reg:
        st.markdown(f"### {t('reg_gestore_title')}")
        nome_az = st.text_input(t('company_label'), key="reg_company")
        nome_g = st.text_input(t('name_label'), key="reg_name")
        cognome_g = st.text_input(t('surname_label'), key="reg_surname")
        pass_g = st.text_input(t('pass_label'), type="password", key="reg_pass")

        if st.button(t('reg_btn'), type="primary"):
            if nome_az and nome_g and cognome_g:
                if nome_az in st.session_state.aziende:
                    st.error("Esiste già un'azienda con questo nome. Scegli un nome differente.")
                else:
                    st.session_state.aziende[nome_az] = {
                        "lista_gestori": [{"nome": nome_g, "cognome": cognome_g, "password": pass_g}],
                        "reparti_custom": ["Cucina", "Sala", "Bar"],
                        "mansioni_custom": ["Chef", "Cameriere", "Barista"],
                        "dipendenti": [
                            {"Nome": "Mario", "Cognome": "Rossi", "Reparto": "Cucina", "Mansione": "Chef", "Ore Max": 40, "Giorni di Riposo": 2},
                            {"Nome": "Luca", "Cognome": "Bianchi", "Reparto": "Sala", "Mansione": "Cameriere", "Ore Max": 36, "Giorni di Riposo": 2}
                        ],
                        "config_orari_attivita": {"giorni_chiusura": [], "turni_definiti": ["Turno Mattina", "Turno Pomeriggio"]},
                        "fabbisogno_per_reparto": {},
                        "registro_assenze": [],
                        "archivio_turni": {},
                        "chat_messaggi": [],
                        "richieste_scambio": [],
                        "wizard_completato": True
                    }
                    salva_dati_locali()
                    imposta_azienda_attiva(nome_az)
                    st.session_state.autenticato_gestore = True
                    st.session_state.gestore_corrente = {"nome": nome_g, "cognome": cognome_g}
                    st.success(f"Azienda '{nome_az}' creata con successo!")
                    st.rerun()
            else:
                st.error("Compila tutti i campi obbligatori.")

def dashboard_gestore():
    st.sidebar.title(f"👔 {st.session_state.azienda_corrente}")
    if st.sidebar.button(t('logout_btn')):
        st.session_state.autenticato_gestore = False
        st.session_state.ruolo_accesso = None
        st.session_state.azienda_corrente = None
        st.rerun()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        t('tab_struttura'), t('tab_staff'), t('tab_fabbisogno'), 
        t('tab_assenze'), t('tab_generatore'), t('tab_impostazioni')
    ])

    with tab1:
        render_tip('tip_struttura')
        st.subheader("📊 Configurazione Reparti e Mansioni")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### {t('reparti_title')}")
            nuovo_rep = st.text_input("Nome Nuovo Reparto")
            if st.button(t('add_reparto')):
                if nuovo_rep and nuovo_rep not in st.session_state.reparti_custom:
                    st.session_state.reparti_custom.append(nuovo_rep)
                    salva_dati_locali()
                    st.rerun()
            st.write(st.session_state.reparti_custom)

        with col2:
            st.markdown(f"#### {t('mansioni_title')}")
            nuova_mans = st.text_input("Nome Nuova Mansione")
            if st.button(t('add_mansione')):
                if nuova_mans and nuova_mans not in st.session_state.mansioni_custom:
                    st.session_state.mansioni_custom.append(nuova_mans)
                    salva_dati_locali()
                    st.rerun()
            st.write(st.session_state.mansioni_custom)

    with tab2:
        render_tip('tip_staff')
        st.subheader("👥 Anagrafica Personale")
        df_dip = pd.DataFrame(st.session_state.dipendenti)
        edited_df = st.data_editor(df_dip, num_rows="dynamic", use_container_width=True)
        if st.button(t('save_changes')):
            st.session_state.dipendenti = edited_df.to_dict(orient="records")
            salva_dati_locali()
            st.success("Staff aggiornato salvato con successo!")

    with tab3:
        render_tip('tip_fabbisogno')
        st.subheader("📈 Fabbisogno Operativo per Reparto")
        rep_selezionato = st.selectbox("Seleziona Reparto:", options=st.session_state.reparti_custom)
        if rep_selezionato:
            df_fabb = get_fabbisogno_reparto_df(rep_selezionato)
            edited_fabb = st.data_editor(df_fabb, num_rows="dynamic", use_container_width=True)
            if st.button("Salva Fabbisogno"):
                st.session_state.fabbisogno_per_reparto[rep_selezionato] = edited_fabb
                salva_dati_locali()
                st.success("Fabbisogno salvato!")

    with tab4:
        render_tip('tip_assenze')
        st.subheader("📅 Gestione Ferie e Assenze")
        st.info("Registra qui ferie o permessi dei dipendenti.")
        dip_nomi = [f"{d['Nome']} {d['Cognome']}" for d in st.session_state.dipendenti]
        if dip_nomi:
            d_scelto = st.selectbox("Seleziona Dipendente:", options=dip_nomi)
            data_ass = st.date_input("Data Assenza")
            motivo = st.selectbox("Motivo:", ["Ferie", "Permesso", "Malattia"])
            if st.button("Registra Assenza"):
                st.session_state.registro_assenze.append({"Dipendente": d_scelto, "Data": str(data_ass), "Motivo": motivo})
                salva_dati_locali()
                st.success("Assenza registrata!")
            st.write(pd.DataFrame(st.session_state.registro_assenze))
        else:
            st.warning("Inserisci prima almeno un dipendente nella scheda Staff.")

    with tab5:
        render_tip('tip_generatore')
        st.subheader("⚡ Motore di Generazione Turni IA")
        if st.button(t('generate_btn'), type="primary", use_container_width=True):
            righe_turni = []
            giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
            for d in st.session_state.dipendenti:
                for g in giorni:
                    righe_turni.append({
                        "Dipendente": f"{d['Nome']} {d['Cognome']}",
                        "Reparto": d['Reparto'],
                        "Giorno": g,
                        "Turno Assegnato": "Turno Mattina"
                    })
            df_risultato = pd.DataFrame(righe_turni)
            st.session_state.griglia_corrente = df_risultato
            st.success("Griglia turni generata con successo!")

        if st.session_state.griglia_corrente is not None:
            st.dataframe(st.session_state.griglia_corrente, use_container_width=True)
            if st.button(t('publish_btn'), type="secondary"):
                st.session_state.archivio_turni["Ultima Pianificazione"] = {
                    "settimana": "Corrente",
                    "dataframe": st.session_state.griglia_corrente
                }
                salva_dati_locali()
                st.success("Pianificazione pubblicata e archiviata per il personale!")

    with tab6:
        st.subheader("⚙️ Impostazioni Avanzate e Backup")
        if st.button("Esporta Database JSON"):
            st.download_json = json.dumps(st.session_state.aziende, ensure_ascii=False, indent=4)
            st.download_button("Scarica file JSON", data=st.download_json, file_name="shiftia_backup.json", mime="application/json")

def dashboard_dipendente():
    st.sidebar.title(f"👤 Operatore: {st.session_state.azienda_corrente}")
    if st.sidebar.button(t('logout_btn')):
        st.session_state.ruolo_accesso = None
        st.session_state.azienda_corrente = None
        st.rerun()

    st.subheader("👋 Benvenuto nel tuo Workspace Dipendente")
    st.info("Qui puoi consultare la pianificazione dei turni pubblicata dalla tua azienda.")

    if st.session_state.archivio_turni:
        for k, v in st.session_state.archivio_turni.items():
            st.markdown(f"### Turni Pubblicati: {k}")
            df_t = v["dataframe"]
            if isinstance(df_t, list):
                df_t = pd.DataFrame(df_t)
            st.dataframe(df_t, use_container_width=True)
    else:
        st.warning("Nessun turno pubblicato al momento dal Gestore.")

# ==========================================
# 7. ROUTING PRINCIPALE
# ==========================================
init_session_state()
inject_custom_css()

if st.session_state.ruolo_accesso is None:
    schermata_landing()
elif st.session_state.ruolo_accesso == "Gestore":
    if not st.session_state.autenticato_gestore:
        schermata_login_gestore()
    else:
        dashboard_gestore()
elif st.session_state.ruolo_accesso == "Dipendente":
    dashboard_dipendente()
