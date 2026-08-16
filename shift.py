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
st.set_page_config(page_title="ShiftIA — Gestione Turni", page_icon="🤖", layout="wide")

DB_FILE = "shiftia_db.json"

# ==========================================
# 1. DIZIONARIO TRADUZIONI MULTILINGUA
# ==========================================
TRANSLATIONS = {
    "IT": {
        "tagline": "La pianificazione dei turni per qualsiasi settore aziendale.",
        "badge": "✨ Intelligenza Artificiale per la gestione del personale",
        "intro_desc": "Configura la tua struttura, definisci i fabbisogni ed esegui la copertura ideale senza buchi o sovrapposizioni.",
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
        "logout_btn": "🚪 Esci Account",
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
        "reg_gestore_title": "📝 Registrazione Nuovo Gestore",
        "pass_label": "Password",
        "name_label": "Nome",
        "surname_label": "Cognome",
        "login_btn": "Entra in ShiftIA 🚀",
        "reg_btn": "Crea Account Gestore 🚀",
        "generate_btn": "🤖 GENERAZIONE OTTIMIZZATA TURNI",
        "publish_btn": "🔒 PUBBLICA PIANIFICAZIONE PER IL PERSONALE",
        # TIPS
        "tip_struttura": "Configura i reparti e le mansioni operative della tua struttura.",
        "tip_staff": "Imposta per ogni collaboratore sia le ore massime che i giorni di riposo spettanti.",
        "tip_fabbisogno": "Imposta quante persone servono per ogni specifico turno nei giorni della settimana.",
        "tip_assenze": "Registra ferie o permessi. L'algoritmo li escluderà dal calcolo turni.",
        "tip_generatore": "L'algoritmo calcola i turni incrociando: Fabbisogno Reparto, Ore Max, Giorni di Riposo Spettanti, Assenze e Giorni di Chiusura.",
        "tip_gestori_mgmt": "Qui puoi aggiornare le credenziali o eliminare gli account gestori esistenti prima di accedere."
    },
    "EN": {
        "tagline": "Shift planning for any business sector.",
        "badge": "✨ Artificial Intelligence for workforce management",
        "intro_desc": "Configure your structure, define requirements and calculate optimal coverage with no gaps or overlaps.",
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
        "logout_btn": "🚪 Log out",
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
        "reg_gestore_title": "📝 Register New Manager",
        "pass_label": "Password",
        "name_label": "First Name",
        "surname_label": "Last Name",
        "login_btn": "Enter ShiftIA 🚀",
        "reg_btn": "Create Manager Account 🚀",
        "generate_btn": "🤖 OPTIMIZED SHIFT GENERATION",
        "publish_btn": "🔒 PUBLISH SCHEDULE TO STAFF",
        # TIPS
        "tip_struttura": "Configure departments and operational tasks for your organization.",
        "tip_staff": "Set both maximum weekly hours and entitlement rest days for each employee.",
        "tip_fabbisogno": "Define how many staff members are required for each specific shift across days of the week.",
        "tip_assenze": "Register leave or time-off. The algorithm will exclude them from shift assignment.",
        "tip_generatore": "The algorithm calculates shifts by cross-referencing: Department Needs, Max Hours, Rest Days, Absences, and Closure Days.",
        "tip_gestori_mgmt": "Here you can update credentials or delete existing manager accounts before logging in."
    },
    "ES": {
        "tagline": "Planificación de turnos para cualquier sector empresarial.",
        "badge": "✨ Inteligencia Artificial para la gestión del personal",
        "intro_desc": "Configura tu estructura, define necesidades y calcula la cobertura ideal sin vacíos ni solapamientos.",
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
        "logout_btn": "🚪 Salir",
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
        "reg_gestore_title": "📝 Registro Nuevo Gestor",
        "pass_label": "Contraseña",
        "name_label": "Nombre",
        "surname_label": "Apellido",
        "login_btn": "Entrar en ShiftIA 🚀",
        "reg_btn": "Crear Cuenta Gestor 🚀",
        "generate_btn": "🤖 GENERACIÓN OPTIMIZADA TURNOS",
        "publish_btn": "🔒 PUBLICAR PROGRAMACIÓN AL PERSONAL",
        # TIPS
        "tip_struttura": "Configura los departamentos y funciones operativas de tu empresa.",
        "tip_staff": "Establece las horas máximas semanales y los días de descanso para cada empleado.",
        "tip_fabbisogno": "Define cuántas personas se necesitan para cada turno específico en los días de la semana.",
        "tip_assenze": "Registra vacaciones o permisos. El algoritmo los excluirá de la programación.",
        "tip_generatore": "El algoritmo calcula los turnos cruzando: Necesidad por Departamento, Horas Máximas, Días de Descanso, Ausencias y Días de Cierre.",
        "tip_gestori_mgmt": "Aquí puedes actualizar credenciales o eliminar cuentas de gestores existentes antes de iniciar sesión."
    }
}

def t(key):
    lang = st.session_state.get("lingua", "IT")
    return TRANSLATIONS.get(lang, TRANSLATIONS["IT"]).get(key, key)

# ==========================================
# 2. PERSISTENZA DATI LOCALE (JSON)
# ==========================================
def salva_dati_locali():
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

    dati = {
        "lista_gestori": st.session_state.lista_gestori,
        "reparti_custom": st.session_state.reparti_custom,
        "mansioni_custom": st.session_state.mansioni_custom,
        "dipendenti": st.session_state.dipendenti,
        "config_orari_attivita": st.session_state.config_orari_attivita,
        "fabbisogno_per_reparto": fabbisogno_json,
        "registro_assenze": st.session_state.registro_assenze,
        "archivio_turni": archivio_json,
        "chat_messaggi": st.session_state.chat_messaggi,
        "richieste_scambio": st.session_state.richieste_scambio
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=4)

def carica_dati_locali():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                dati = json.load(f)
                st.session_state.lista_gestori = dati.get("lista_gestori", [])
                st.session_state.reparti_custom = dati.get("reparti_custom", [])
                st.session_state.mansioni_custom = dati.get("mansioni_custom", [])
                st.session_state.dipendenti = dati.get("dipendenti", [])
                st.session_state.config_orari_attivita = dati.get("config_orari_attivita", {
                    "giorni_chiusura": [],
                    "turni_definiti": ["Turno Mattina", "Turno Pomeriggio", "Turno Notte"]
                })
                
                fab_raw = dati.get("fabbisogno_per_reparto", {})
                fab_restored = {}
                for k, v in fab_raw.items():
                    fab_restored[k] = pd.DataFrame(v) if isinstance(v, list) else v
                st.session_state.fabbisogno_per_reparto = fab_restored

                st.session_state.registro_assenze = dati.get("registro_assenze", [])
                
                arc_raw = dati.get("archivio_turni", {})
                arc_restored = {}
                for k, v in arc_raw.items():
                    arc_restored[k] = {
                        "settimana": v["settimana"],
                        "dataframe": pd.DataFrame(v["dataframe"]) if isinstance(v["dataframe"], list) else v["dataframe"]
                    }
                st.session_state.archivio_turni = arc_restored
                st.session_state.chat_messaggi = dati.get("chat_messaggi", [])
                st.session_state.richieste_scambio = dati.get("richieste_scambio", [])
        except Exception as e:
            st.error(f"Errore durante il caricamento dei dati salvati: {e}")

# ==========================================
# 3. INIZIALIZZAZIONE SESSION STATE
# ==========================================
def safe_int(val):
    if pd.isna(val) or val is None:
        return 0
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0

def init_session_state():
    if "lingua" not in st.session_state:
        st.session_state.lingua = "IT"

    if "show_tips" not in st.session_state:
        st.session_state.show_tips = True

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

        .user-welcome-box {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border-radius: 16px;
            padding: 20px;
            color: white;
            margin-bottom: 20px;
            border-left: 5px solid #38bdf8;
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
# 5. GENERATORE IMMAGINE TURNI
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
# 6. LANDING PAGE
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
# 7. AUTHENTICATION & MANAGEMENT GESTORI
# ==========================================
def schermata_auth_gestore():
    col_back, col_lang = st.columns([4, 1])
    with col_back:
        if st.button(t('back_btn')):
            st.session_state.ruolo_accesso = None
            st.rerun()
    with col_lang:
        lang_choice = st.selectbox(
            "🌐 Lingua",
            options=["IT 🇮🇹", "EN 🇬🇧", "ES 🇪🇸"],
            index=["IT", "EN", "ES"].index(st.session_state.lingua),
            key="select_lang_auth"
        )
        st.session_state.lingua = lang_choice.split()[0]

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # REGISTRAZIONE NUOVO GESTORE
    with col_right:
        st.subheader(t("reg_gestore_title"))
        with st.form("form_reg_gestore", clear_on_submit=True):
            n_g = st.text_input(t("name_label"))
            c_g = st.text_input(t("surname_label"))
            pwd_g = st.text_input(t("pass_label"), type="password")
            btn_reg = st.form_submit_button(t("reg_btn"), use_container_width=True)

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
                    salva_dati_locali()
                    st.success("✅ Gestore registrato con successo!")
                    st.rerun()
                else:
                    st.warning("⚠️ Compila tutti i campi obbligatori.")

    # LOGIN GESTORE
    with col_left:
        st.subheader(t("login_gestore_title"))
        if not st.session_state.lista_gestori:
            st.info("ℹ️ Nessun gestore registrato. Registra il primo account nel modulo a fianco.")
        else:
            opzioni_gestori = [f"{g['nome']} {g['cognome']}" for g in st.session_state.lista_gestori]
            with st.form("form_login_gestore", clear_on_submit=False):
                gestore_scelto_str = st.selectbox("Seleziona il tuo Profilo Gestore:", options=opzioni_gestori)
                pwd_in = st.text_input(t("pass_label"), type="password")
                btn_log = st.form_submit_button(t("login_btn"), use_container_width=True)

                if btn_log:
                    idx = opzioni_gestori.index(gestore_scelto_str)
                    target_g = st.session_state.lista_gestori[idx]
                    
                    if pwd_in == target_g["password"]:
                        st.session_state.gestore_corrente = target_g
                        st.session_state.autenticato_gestore = True
                        st.success(f"Benvenuto {target_g['nome']}!")
                        st.rerun()
                    else:
                        st.error("❌ Password errata.")

    # GESTIONE ACCOUNT GESTORI
    if st.session_state.lista_gestori:
        st.markdown("---")
        st.subheader(t("gestori_mgmt_title"))
        render_tip("tip_gestori_mgmt")

        opzioni_g = [f"{g['nome']} {g['cognome']}" for g in st.session_state.lista_gestori]
        g_scelto_str = st.selectbox("Seleziona Gestore da Modificare o Eliminare:", options=opzioni_g, key="select_gestore_mgmt_auth")
        idx_g = opzioni_g.index(g_scelto_str)
        target_gestore = st.session_state.lista_gestori[idx_g]

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"##### {t('edit_gestore')}")
            with st.form("form_edit_gestore_auth"):
                n_mod = st.text_input(t("name_label"), value=target_gestore["nome"])
                c_mod = st.text_input(t("surname_label"), value=target_gestore["cognome"])
                p_mod = st.text_input(t("pass_label"), value=target_gestore["password"], type="password")
                
                if st.form_submit_button(t("save_changes"), use_container_width=True):
                    target_gestore["nome"] = n_mod.strip()
                    target_gestore["cognome"] = c_mod.strip()
                    target_gestore["password"] = p_mod.strip()
                    salva_dati_locali()
                    st.success("✅ Dati del Gestore aggiornati!")
                    st.rerun()

        with col_m2:
            st.markdown(f"##### {t('del_gestore')}")
            st.warning("⚠️ L'eliminazione è immediata ed irreversibile.")
            if st.button(t("del_gestore"), type="primary", use_container_width=True, key="btn_del_gestore_auth"):
                st.session_state.lista_gestori.pop(idx_g)
                salva_dati_locali()
                st.success("✅ Gestore eliminato con successo!")
                st.rerun()

# ==========================================
# 8. AREA GESTORE
# ==========================================
def render_area_gestore():
    top1, top2, top3 = st.columns([3, 1, 1])
    with top2:
        lang_choice = st.selectbox(
            "🌐 Lingua",
            options=["IT 🇮🇹", "EN 🇬🇧", "ES 🇪🇸"],
            index=["IT", "EN", "ES"].index(st.session_state.lingua),
            key="select_lang_manager"
        )
        st.session_state.lingua = lang_choice.split()[0]
    with top3:
        if st.button(t("logout_btn"), use_container_width=True):
            st.session_state.autenticato_gestore = False
            st.session_state.gestore_corrente = None
            st.rerun()

    dati = st.session_state.gestore_corrente
    st.markdown(
        f"""
        <div class="user-welcome-box">
            <h2 style="margin:0;">{t('panel_title')} — {dati['nome']} {dati['cognome']} 👋</h2>
            <p style="margin:4px 0 0 0; color:#cbd5e1;">Pianificazione turni e gestione della forza lavoro.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    t1, t2, t3, t4, t5, t6 = st.tabs([
        t("tab_struttura"),
        t("tab_staff"),
        t("tab_fabbisogno"),
        t("tab_assenze"),
        t("tab_generatore"),
        t("tab_impostazioni")
    ])

    # --- TAB 1: STRUTTURA AZIENDALE ---
    with t1:
        st.subheader("📊 Definizione Reparti, Mansioni e Turni")
        render_tip("tip_struttura")

        col_r, col_m = st.columns(2)
        with col_r:
            st.markdown(f"##### {t('reparti_title')}")
            with st.form("form_add_reparto", clear_on_submit=True):
                n_r = st.text_input("Nome Reparto/Area")
                btn_r = st.form_submit_button(t("add_reparto"), use_container_width=True)
                if btn_r and n_r.strip():
                    if n_r.strip() not in st.session_state.reparti_custom:
                        st.session_state.reparti_custom.append(n_r.strip())
                        salva_dati_locali()
                        st.success(f"Aggiunto reparto: '{n_r.strip()}'")
                        st.rerun()
            
            if st.session_state.reparti_custom:
                for r in st.session_state.reparti_custom:
                    st.write(f"• **{r}**")
            else:
                st.info("Nessun reparto attualmente configurato.")

        with col_m:
            st.markdown(f"##### {t('mansioni_title')}")
            with st.form("form_add_mansione", clear_on_submit=True):
                n_m = st.text_input("Nome Mansione/Ruolo")
                btn_m = st.form_submit_button(t("add_mansione"), use_container_width=True)
                if btn_m and n_m.strip():
                    if n_m.strip() not in st.session_state.mansioni_custom:
                        st.session_state.mansioni_custom.append(n_m.strip())
                        salva_dati_locali()
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
            lista_t = [t_item.strip() for t_item in nuovi_turni_str.split(",") if t_item.strip()]
            st.session_state.config_orari_attivita["turni_definiti"] = lista_t
            salva_dati_locali()
            st.success("✅ Tipologie di turno aggiornate e salvate!")

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
            salva_dati_locali()
            st.success("✅ Salva configurazione chiusure.")

    # --- TAB 2: STAFF & ANAGRAFICA ---
    with t2:
        st.subheader("👥 Anagrafica Personale & Regole Contrattuali")
        render_tip("tip_staff")

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
                        salva_dati_locali()
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
                if st.button(t("delete_btn"), type="primary", use_container_width=True, key="btn_del_dip"):
                    idx_del = opzioni_dip.index(dip_scelto_del)
                    rimosso = st.session_state.dipendenti.pop(idx_del)
                    salva_dati_locali()
                    st.success(f"✅ **{rimosso['Nome']} {rimosso['Cognome']}** eliminato!")
                    st.rerun()
        else:
            st.info("Nessun membro del personale inserito.")

    # --- TAB 3: FABBISOGNO OPERATIVO ---
    with t3:
        st.subheader("📈 Fabbisogno del Personale per Reparto")
        render_tip("tip_fabbisogno")
        
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
                if st.button("💾 Salva Fabbisogno", key="btn_save_fab", use_container_width=True):
                    salva_dati_locali()
                    st.success("✅ Fabbisogno salvato con successo!")

    # --- TAB 4: CALENDARIO & ASSENZE ---
    with t4:
        st.subheader("📅 Registro Assenze & Disponibilità")
        render_tip("tip_assenze")

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
                    salva_dati_locali()
                    st.success(f"✅ Assenza salvata per {dip_scelto}!")
                    st.rerun()
        else:
            st.info("Nessun dipendente a cui assegnare un'assenza.")

    # --- TAB 5: GENERATORE IA ---
    with t5:
        st.subheader("⚡ Algoritmo Generatore Turni Intelligente")
        render_tip("tip_generatore")

        data_riferimento = st.date_input("Seleziona data di inizio settimana:", datetime.now() + timedelta(days=7))
        lunedi_scelto = data_riferimento - timedelta(days=data_riferimento.weekday())

        if st.button(t("generate_btn"), type="primary", use_container_width=True):
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

                # Step 1: Pre-compilazione Chiusure ed Assenze
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

                            dip_candidati = [
                                d for d in st.session_state.dipendenti 
                                if str(d.get("Reparto")).strip().lower() == str(rep_nome).strip().lower()
                            ]

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
            
            if st.button(t("publish_btn"), type="primary", use_container_width=True):
                k = f"Settimana_{lunedi_scelto.strftime('%d_%m_%Y')}"
                st.session_state.archivio_turni[k] = {
                    "settimana": lunedi_scelto.strftime('%d/%m/%Y'),
                    "dataframe": df_edit
                }
                salva_dati_locali()
                st.success("✅ Pianificazione pubblicata e salvata con successo!")

    # --- TAB 6: ARCHIVIO & IMPOSTAZIONI SISTEMA ---
    with t6:
        st.subheader("⚙️ Impostazioni & Archivio Turni")
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
# 9. AREA DIPENDENTE / OPERATORE
# ==========================================
def render_area_dipendente():
    top1, top2 = st.columns([4, 1])
    with top2:
        if st.button(t("logout_btn"), use_container_width=True):
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
                        salva_dati_locali()
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
                    salva_dati_locali()
                    st.rerun()

# ==========================================
# 10. ROUTER PRINCIPALE
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
