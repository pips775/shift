import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import io
import calendar
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
        "intro_desc": "Crea o seleziona la tua Azienda / Workspace simulato per pianificare i turni in totale autonomia senza interferenze con altri tester.",
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
        "gestori_mgmt_title": "⚙️ Gestione Account Gestori Registrati",
        "edit_gestore": "✏️ Modifica Gestore Selezionato",
        "del_gestore": "🗑️ Elimina Gestore Selezionato",
        "save_changes": "💾 Salva Modifiche",
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
        "tip_generatore": "L'algoritmo calcola i turni incrociando: Fabbisogno Reparto, Ore Max, Giorni di Riposo Spettanti, Assenze e Giorni di Chiusura.",
        "tip_gestori_mgmt": "Qui puoi aggiornare le credenziali o eliminare gli account gestori esistenti per questa azienda."
    },
    "EN": {
        "tagline": "Shift planning for any business sector.",
        "badge": "✨ Artificial Intelligence for workforce management",
        "intro_desc": "Create or select your simulated Company / Workspace to schedule shifts independently without interfering with other testers.",
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
        "gestori_mgmt_title": "⚙️ Registered Managers Account Management",
        "edit_gestore": "✏️ Edit Selected Manager",
        "del_gestore": "🗑️ Delete Selected Manager",
        "save_changes": "💾 Save Changes",
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
        "tip_generatore": "The algorithm calculates shifts by cross-referencing: Department Needs, Max Hours, Rest Days, Absences, and Closure Days.",
        "tip_gestori_mgmt": "Here you can update credentials or delete existing manager accounts before logging in."
    },
    "ES": {
        "tagline": "Planificación de turnos para cualquier sector empresarial.",
        "badge": "✨ Inteligencia Artificial para la gestión del personal",
        "intro_desc": "Crea o selecciona tu Empresa / Espacio simulado para planificar turnos de forma independiente y sin interferencias.",
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
        "gestori_mgmt_title": "⚙️ Gestión de Cuentas de Gestores Registrados",
        "edit_gestore": "✏️ Editar Gestor Seleccionado",
        "del_gestore": "🗑️ Eliminar Gestor Seleccionado",
        "save_changes": "💾 Guardar Cambios",
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
        "tip_generatore": "El algoritmo calcula los turnos cruzando: Necesidad por Departamento, Horas Máximas, Días de Descanso, Ausencias y Días de Cierre.",
        "tip_gestori_mgmt": "Aquí puedes actualizar credenciales o eliminar cuentas de gestores existentes antes de iniciar sesión."
    }
}

def t(key):
    lang = st.session_state.get("lingua", "IT")
    return TRANSLATIONS.get(lang, TRANSLATIONS["IT"]).get(key, key)

def ottieni_etichetta_gestore(g):
    if isinstance(g, dict):
        nome = g.get('nome', '')
        cognome = g.get('cognome', '')
        res = f"{nome} {cognome}".strip()
        return res if res else "Gestore Senza Nome"
    return str(g)

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
        except Exception as e:
            st.error(f"Errore durante il caricamento dei dati salvati: {e}")
            st.session_state.aziende = {}
    else:
        st.session_state.aziende = {}

def imposta_azienda_attiva(az_selezionata_login):
    if not az_selezionata_login:
        st.session_state.azienda_corrente = None
        st.session_state.lista_gestori = []
        return

    dati_az = None
    if "aziende" in st.session_state and isinstance(st.session_state.aziende, dict):
        dati_az = st.session_state.aziende.get(az_selezionata_login)

    if not dati_az or not isinstance(dati_az, dict):
        st.session_state.azienda_corrente = None
        st.session_state.lista_gestori = []
        return

    st.session_state.azienda_corrente = az_selezionata_login
    st.session_state.lista_gestori = dati_az.get("lista_gestori", [])
    st.session_state.reparti_custom = dati_az.get("reparti_custom", [])
    st.session_state.mansioni_custom = dati_az.get("mansioni_custom", [])
    st.session_state.dipendenti = dati_az.get("dipendenti", [])
    st.session_state.config_orari_attivita = dati_az.get("config_orari_attivita", {
        "giorni_chiusura": [],
        "turni_definiti": ["Turno Mattina", "Turno Pomeriggio", "Turno Notte"]
    })
    
    fabb_raw = dati_az.get("fabbisogno_per_reparto", {})
    fabb_df = {}
    for k, v in fabb_raw.items():
        if isinstance(v, list):
            fabb_df[k] = pd.DataFrame(v)
        elif isinstance(v, pd.DataFrame):
            fabb_df[k] = v
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
    st.session_state.wizard_completato = dati_az.get("wizard_completato", False)

def elimina_azienda(nome_azienda):
    if "aziende" in st.session_state and nome_azienda in st.session_state.aziende:
        del st.session_state.aziende[nome_azienda]
        
        if st.session_state.get("azienda_corrente") == nome_azienda:
            st.session_state.azienda_corrente = None
            st.session_state.lista_gestori = []
            st.session_state.autenticato_gestore = False
            st.session_state.gestore_corrente = None
            st.session_state.dipendente_corrente = None
            st.session_state.ruolo_accesso = None
            
        salva_dati_locali()

# ==========================================
# 3. INIZIALIZZAZIONE SESSION STATE
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
# 4. STILI CSS CUSTOM
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

        .wizard-box {
            background: #1e293b;
            border: 1px solid #38bdf8;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
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
# 5. LANDING PAGE CON BANDIERINE LINGUA
# ==========================================
def schermata_landing():
    # Barra superiore con bandierine per la selezione della lingua
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
                st.success(f"Azienda '{az_scelta}' eliminata con successo!")
                st.rerun()

        if st.button("👉 Seleziona questa Azienda", type="secondary", use_container_width=True):
            imposta_azienda_attiva(az_scelta)
            st.success(f"Azienda attiva impostata su: **{az_scelta}**")
            st.rerun()
    else:
        st.info("ℹ️ Nessuna azienda ancora creata nel sistema. Inizia creandone una per i tuoi test!")

    st.markdown("---")

    if st.session_state.azienda_corrente:
        st.success(f"🏢 **Azienda Attualmente Selezionata:** {st.session_state.azienda_corrente}")
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
        st.warning("⚠️ Seleziona un'azienda dall'elenco o creane una nuova nel pulsante Gestore di seguito per proseguire.")
        if st.button("🔑 Vai alla Registrazione Nuova Azienda / Accesso Gestore", type="primary", use_container_width=True):
            st.session_state.ruolo_accesso = "Gestore"
            st.rerun()

    render_footer()

# Inizializzazione ed esecuzione principale
init_session_state()
inject_custom_css()

if st.session_state.ruolo_accesso is None:
    schermata_landing()
else:
    st.write(f"Area riservata per il ruolo: {st.session_state.ruolo_accesso}")
    if st.button("Torna alla Home"):
        st.session_state.ruolo_accesso = None
        st.rerun()
