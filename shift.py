import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import io
import calendar
import json
import os
import random
from datetime import datetime, timedelta

# Configurazione pagina Streamlit
st.set_page_config(page_title="ShiftIA — Gestione Turni Multi-Azienda", page_icon="🤖", layout="wide")

DB_FILE = "shiftia_db.json"

# ==========================================
# 1. DIZIONARIO TRADUZIONI MULTILINGUA
# ==========================================
TRANSLATIONS = {
    "IT": {
        "tagline": "La pianificazione intelligente dei turni per qualsiasi settore aziendale.",
        "badge": "✨ Intelligenza Artificiale & Workforce Management",
        "intro_desc": "Crea o seleziona la tua Azienda / Workspace simulato per pianificare i turni in totale autonomia.",
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
        "panel_title": "Pannello di Controllo Gestore",
        "reparti_title": "🏢 Reparti / Settori",
        "mansioni_title": "🛠️ Mansioni / Qualifiche",
        "add_reparto": "➕ Aggiungi Reparto",
        "add_mansione": "➕ Aggiungi Mansione",
        "delete_btn": "🗑️ Rimuovi",
        "save_changes": "💾 Salva Modifiche",
        "login_gestore_title": "🔑 Accesso Gestore & Aziende",
        "reg_gestore_title": "📝 Registrazione Nuova Azienda / Workspace",
        "pass_label": "Password",
        "name_label": "Nome Gestore",
        "surname_label": "Cognome Gestore",
        "company_label": "Nome Azienda / Workspace",
        "login_btn": "Entra in ShiftIA 🚀",
        "reg_btn": "Crea Azienda e Account 🚀",
        "generate_btn": "🤖 GENERAZIONE OTTIMIZZATA TURNI",
        "publish_btn": "🔒 PUBBLICA PIANIFICAZIONE PER IL PERSONALE",
        "tip_struttura": "Configura i reparti e le mansioni operative della tua struttura.",
        "tip_staff": "Usa le spunte nella tabella per assegnare o rimuovere le mansioni ai dipendenti in tempo reale.",
        "tip_fabbisogno": "Imposta quante persone servono per ogni specifico turno nei giorni della settimana.",
        "tip_assenze": "Registra ferie o permessi. L'algoritmo li escluderà dal calcolo turni.",
        "tip_generatore": "L'algoritmo calcola i turni incrociando: Fabbisogno Reparto, Ore Max, Giorni di Riposo e Assenze."
    },
    "EN": {
        "tagline": "Smart shift planning for any business sector.",
        "badge": "✨ Artificial Intelligence & Workforce Management",
        "intro_desc": "Create or select your simulated Company / Workspace to schedule shifts independently.",
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
        "panel_title": "Manager Control Panel",
        "reparti_title": "🏢 Departments / Sectors",
        "mansioni_title": "🛠️ Roles / Tasks",
        "add_reparto": "➕ Add Department",
        "add_mansione": "➕ Add Role",
        "delete_btn": "🗑️ Remove",
        "save_changes": "💾 Save Changes",
        "login_gestore_title": "🔑 Manager Login & Companies",
        "reg_gestore_title": "📝 Register New Company / Workspace",
        "pass_label": "Password",
        "name_label": "Manager First Name",
        "surname_label": "Manager Last Name",
        "company_label": "Company / Workspace Name",
        "login_btn": "Enter ShiftIA 🚀",
        "reg_btn": "Create Company & Account 🚀",
        "generate_btn": "🤖 OPTIMIZED SHIFT GENERATION",
        "publish_btn": "🔒 PUBLISH SCHEDULE TO STAFF",
        "tip_struttura": "Configure departments and operational tasks for your organization.",
        "tip_staff": "Use the checkboxes in the table to assign or remove roles from employees.",
        "tip_fabbisogno": "Define how many staff members are required for each specific shift.",
        "tip_assenze": "Register leave or time-off. The algorithm will exclude them from shift assignment.",
        "tip_generatore": "The algorithm calculates shifts cross-referencing Department Needs, Max Hours, and Absences."
    },
    "ES": {
        "tagline": "Planificación inteligente de turnos para cualquier sector.",
        "badge": "✨ Inteligencia Artificial y Gestión de Personal",
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
        "panel_title": "Panel de Control Gestor",
        "reparti_title": "🏢 Departamentos / Áreas",
        "mansioni_title": "🛠️ Funciones / Puestos",
        "add_reparto": "➕ Añadir Departamento",
        "add_mansione": "➕ Añadir Función",
        "delete_btn": "🗑️ Eliminar",
        "save_changes": "💾 Guardar Cambios",
        "login_gestore_title": "🔑 Acceso Gestor y Empresas",
        "reg_gestore_title": "📝 Registro Nueva Empresa / Espacio",
        "pass_label": "Contraseña",
        "name_label": "Nombre del Gestor",
        "surname_label": "Apellido del Gestor",
        "company_label": "Nombre de la Empresa",
        "login_btn": "Entrar en ShiftIA 🚀",
        "reg_btn": "Crear Empresa y Cuenta 🚀",
        "generate_btn": "🤖 GENERACIÓN OPTIMIZADA TURNOS",
        "publish_btn": "🔒 PUBLICAR PROGRAMACIÓN AL PERSONAL",
        "tip_struttura": "Configura los departamentos y funciones operativas de tu empresa.",
        "tip_staff": "Usa las casillas en la tabla para asignar o quitar funciones a los empleados.",
        "tip_fabbisogno": "Define cuántas personas se necesitan para cada turno específico.",
        "tip_assenze": "Registra vacaciones o permisos. El algoritmo los excluirá.",
        "tip_generatore": "El algoritmo calcula los turnos cruzando necesidades de departamento y ausencias."
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
        except Exception as e:
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
            st.session_state.ruolo_accesso = None
        salva_dati_locali()

# ==========================================
# 3. ALGORITMO DI GENERAZIONE TURNI INTELLIGENTE
# ==========================================
def genera_turni_ottimizzati():
    dipendenti = st.session_state.get("dipendenti", [])
    fabbisogno_per_reparto = st.session_state.get("fabbisogno_per_reparto", {})
    turni_definiti = st.session_state.config_orari_attivita.get("turni_definiti", ["Turno Mattina", "Turno Pomeriggio"])
    giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    giorni_chiusura = st.session_state.config_orari_attivita.get("giorni_chiusura", [])
    assenze = st.session_state.get("registro_assenze", [])
    
    if not dipendenti:
        return None

    ore_accumulate = {d.get("id", i): 0 for i, d in enumerate(dipendenti)}
    programmazione = []

    for giorno in giorni:
        if giorno in giorni_chiusura:
            continue
            
        pool = dipendenti.copy()
        random.shuffle(pool)
        lavorato_oggi = set()

        dipendenti_disponibili = []
        for d in pool:
            d_nome = f"{d.get('nome', '')} {d.get('cognome', '')}".strip()
            in_ferie = any(a.get("Dipendente") == d_nome and a.get("Giorno") == giorno for a in assenze)
            if not in_ferie:
                dipendenti_disponibili.append(d)

        for turno in turni_definiti:
            for nome_reparto, df_fabb in fabbisogno_per_reparto.items():
                if isinstance(df_fabb, pd.DataFrame) and giorno in df_fabb.columns:
                    row = df_fabb[df_fabb['Turno'] == turno]
                    if not row.empty:
                        try:
                            richiesta = int(row.iloc[0][giorno])
                        except:
                            richiesta = 0
                        
                        assegnati_turno = 0
                        for d in dipendenti_disponibili:
                            d_id = d.get("id", d.get("nome", ""))
                            if assegnati_turno >= richiesta:
                                break
                            
                            if d_id not in lavorato_oggi and ore_accumulate[d_id] < 40:
                                programmazione.append({
                                    "Dipendente": f"{d.get('nome', '')} {d.get('cognome', '')}".strip(),
                                    "Giorno": giorno,
                                    "Turno": turno,
                                    "Reparto": nome_reparto
                                })
                                lavorato_oggi.add(d_id)
                                ore_accumulate[d_id] += 8
                                assegnati_turno += 1
                                
    if not programmazione:
        return None
        
    df_result = pd.DataFrame(programmazione)
    giorni_ordinati = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    
    griglia_pivot = df_result.pivot_table(
        index="Dipendente", 
        columns="Giorno", 
        values="Turno", 
        aggfunc=lambda x: ' / '.join(x)
    )
    
    colonne_presenti = [g for g in giorni_ordinati if g in griglia_pivot.columns]
    griglia_pivot = griglia_pivot.reindex(columns=colonne_presenti).fillna("RIPOSO")
    return griglia_pivot

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
# 5. STILI CSS CUSTOM PROFESSIONALI
# ==========================================
def inject_custom_css():
    st.markdown(
        """
        <style>
        /* Stili Generali e Tema Dashboard */
        .stApp {
            background-color: #0b0f19;
            color: #f8fafc;
        }
        .welcome-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 16px;
            padding: 36px;
            text-align: center;
            color: #ffffff;
            margin-bottom: 28px;
            border: 1px solid rgba(56, 189, 248, 0.2);
            box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.5);
        }
        .welcome-title {
            font-size: 44px;
            font-weight: 800;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        }
        .wizard-box {
            background: #1e293b;
            border: 1.5px solid #38bdf8;
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px rgba(56, 189, 248, 0.1);
        }
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(56, 189, 248, 0.25);
        }
        /* Personalizzazione Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #111827;
            padding: 10px;
            border-radius: 12px;
            border: 1px solid #1f2937;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1f2937;
            border-radius: 8px;
            color: #9ca3af;
            font-weight: 600;
            padding: 10px 18px;
            border: none;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%);
            color: white !important;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
        }
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_footer():
    st.markdown(
        f"""
        <br><hr style="border-color: #1e293b;">
        <p style='text-align: center; font-size: 13px; color: #64748b;'>
            <b>ShiftIA</b> — {t('footer_text')}
        </p>
        """,
        unsafe_allow_html=True
    )

def genera_immagine_turni(df):
    width, height = 1200, 110 + (max(len(df), 1) * 55)
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    az_nome = st.session_state.get("azienda_corrente", "Azienda")
    draw.rectangle([(0, 0), (width, 60)], fill=(15, 23, 42))
    draw.text((20, 20), f"SHIFTIA — PROGRAMMAZIONE TURNI ({az_nome.upper()})", fill=(255, 255, 255))
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
            elif "Ferie" in val or "Assenza" in val or "Malattia" in val:
                bg_color = (254, 243, 199)
            draw.rectangle([(j * col_width, y_top), ((j + 1) * col_width, y_top + 55)], fill=bg_color, outline=(226, 232, 240))
            draw.text((j * col_width + 6, y_top + 10), val[:16], fill=(15, 23, 42))

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()

# ==========================================
# 6. WIZARD E INTERFACCE
# ==========================================
def render_interactive_wizard():
    az = st.session_state.azienda_corrente
    step = st.session_state.wizard_step
    st.markdown(
        f"""
        <div class="wizard-box">
            <h2 style="margin:0; color:#38bdf8;">🧙‍♂️ Configurazione Guidata Iniziale — {az}</h2>
            <p style="color:#cbd5e1; margin-top:6px;">Configura la tua struttura in 4 semplici passaggi.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.progress(step / 4, text=f"Passaggio {step} di 4")

    if step == 1:
        st.subheader("Passo 1: Aggiungi i Reparti / Settori Operativi")
        reparti_str = st.text_input("Inserisci i reparti separati da virgola:", value="Cassa, Sala, Magazzino")
        if st.button("Avanti ➡️ (Passo 2)", type="primary", use_container_width=True):
            st.session_state.reparti_custom = [r.strip() for r in reparti_str.split(",") if r.strip()]
            st.session_state.wizard_step = 2
            salva_dati_locali()
            st.rerun()
    elif step == 2:
        st.subheader("Passo 2: Definisci le Mansioni / Qualifiche")
        mansioni_str = st.text_input("Inserisci le mansioni separate da virgola:", value="Operatore, Responsabile, Assistente")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Indietro", use_container_width=True):
                st.session_state.wizard_step = 1
                st.rerun()
        with c2:
            if st.button("Avanti ➡️ (Passo 3)", type="primary", use_container_width=True):
                st.session_state.mansioni_custom = [m.strip() for m in mansioni_str.split(",") if m.strip()]
                st.session_state.wizard_step = 3
                salva_dati_locali()
                st.rerun()
    elif step == 3:
        st.subheader("Passo 3: Configura i Turni Settimanali")
        turni_str = st.text_input("Inserisci i turni separati da virgola:", value="Turno Mattina, Turno Pomeriggio, Turno Notte")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Indietro", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()
        with c2:
            if st.button("Avanti ➡️ (Passo 4)", type="primary", use_container_width=True):
                st.session_state.config_orari_attivita["turni_definiti"] = [t_item.strip() for t_item in turni_str.split(",") if t_item.strip()]
                st.session_state.wizard_step = 4
                salva_dati_locali()
                st.rerun()
    elif step == 4:
        st.subheader("Passo 4: Giorni di Chiusura Settimanale")
        giorni_comp = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        chiusure = st.multiselect("Giorni di chiusura:", options=giorni_comp, default=[])
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Indietro", use_container_width=True):
                st.session_state.wizard_step = 3
                st.rerun()
        with c2:
            if st.button("🎉 Completa Configurazione & Accedi", type="primary", use_container_width=True):
                st.session_state.config_orari_attivita["giorni_chiusura"] = chiusure
                st.session_state.wizard_completato = True
                salva_dati_locali()
                st.success("✅ Configurazione iniziale completata!")
                st.rerun()

def schermata_landing():
    top_col1, top_col2 = st.columns([3, 1])
    with top_col2:
        lang_choice = st.selectbox("🌐 Lingua / Language", options=["IT 🇮🇹", "EN 🇬🇧", "ES 🇪🇸"], index=["IT", "EN", "ES"].index(st.session_state.lingua))
        st.session_state.lingua = lang_choice.split()[0]

    st.markdown(
        f"""
        <div class="welcome-card">
            <div style="font-size:14px; color:#38bdf8; font-weight:700; margin-bottom:8px; text-transform: uppercase; letter-spacing: 1px;">{t('badge')}</div>
            <div class="welcome-title">🤖 ShiftIA</div>
            <div style="font-size:19px; color:#cbd5e1; margin-bottom:14px;"><b>{t('tagline')}</b></div>
            <p style="font-size: 15px; color: #94a3b8; max-width: 680px; margin: 0 auto; line-height: 1.5;">{t('intro_desc')}</p>
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
            if st.button("🗑️ Elimina", help="Elimina azienda", use_container_width=True):
                elimina_azienda(az_scelta)
                st.success(f"Azienda '{az_scelta}' eliminata!")
                st.rerun()

        if st.button("👉 Seleziona questa Azienda", type="secondary", use_container_width=True):
            imposta_azienda_attiva(az_scelta)
            st.success(f"Azienda attiva: **{az_scelta}**")
            st.rerun()
    else:
        st.info("ℹ️ Nessuna azienda ancora creata. Creane una qui sotto!")

    st.markdown("---")
    st.subheader("📝 Registra una Nuova Azienda / Workspace")
    with st.form("form_reg_azienda"):
        nuova_az = st.text_input(t("company_label"))
        nome_g = st.text_input(t("name_label"))
        cognome_g = st.text_input(t("surname_label"))
        pass_g = st.text_input(t("pass_label"), type="password")
        submit_az = st.form_submit_button(t("reg_btn"), use_container_width=True)

        if submit_az:
            if nuova_az and nome_g and pass_g:
                st.session_state.aziende[nuova_az] = {
                    "lista_gestori": [{"nome": nome_g, "cognome": cognome_g, "password": pass_g}],
                    "reparti_custom": ["Cassa", "Sala"],
                    "mansioni_custom": ["Operatore", "Responsabile"],
                    "dipendenti": [],
                    "config_orari_attivita": {"giorni_chiusura": [], "turni_definiti": ["Turno Mattina", "Turno Pomeriggio"]},
                    "fabbisogno_per_reparto": {},
                    "registro_assenze": [],
                    "archivio_turni": [],
                    "chat_messaggi": [],
                    "richieste_scambio": [],
                    "wizard_completato": False
                }
                imposta_azienda_attiva(nuova_az)
                st.session_state.autenticato_gestore = True
                st.session_state.ruolo_accesso = "Gestore"
                salva_dati_locali()
                st.success(f"Azienda '{nuova_az}' creata con successo!")
                st.rerun()
            else:
                st.error("Compila tutti i campi obbligatori.")

    if st.session_state.azienda_corrente:
        st.markdown("---")
        st.success(f"🏢 **Azienda Attualmente Selezionata:** {st.session_state.azienda_corrente}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t('role_employee_btn'), use_container_width=True, type="primary"):
                st.session_state.ruolo_accesso = "Dipendente"
                st.rerun()
        with col2:
            if st.button(t('role_manager_btn'), use_container_width=True):
                st.session_state.autenticato_gestore = True
                st.session_state.ruolo_accesso = "Gestore"
                st.rerun()

    render_footer()

def pannello_gestore():
    st.sidebar.title(t("panel_title"))
    st.sidebar.write(f"🏢 Azienda: **{st.session_state.azienda_corrente}**")
    
    if st.sidebar.button(t("logout_btn"), use_container_width=True):
        st.session_state.ruolo_accesso = None
        st.session_state.autenticato_gestore = False
        st.session_state.azienda_corrente = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.checkbox("Mostra suggerimenti IA", value=st.session_state.show_tips, key="show_tips")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        t("tab_struttura"),
        t("tab_staff"),
        t("tab_fabbisogno"),
        t("tab_assenze"),
        t("tab_generatore"),
        t("tab_impostazioni")
    ])

    with tab1:
        render_tip("tip_struttura")
        st.subheader(t("reparti_title"))
        col_r1, col_r2 = st.columns([3, 1])
        with col_r1:
            nuovo_rep = st.text_input("Nome Nuovo Reparto", key="input_nuovo_rep")
        with col_r2:
            st.write("")
            if st.button(t("add_reparto"), use_container_width=True):
                if nuovo_rep and nuovo_rep not in st.session_state.reparti_custom:
                    st.session_state.reparti_custom.append(nuovo_rep)
                    salva_dati_locali()
                    st.rerun()

        st.write("Reparti attivi:", st.session_state.reparti_custom)

        st.subheader(t("mansioni_title"))
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            nuova_mans = st.text_input("Nome Nuova Mansione", key="input_nuova_mans")
        with col_m2:
            st.write("")
            if st.button(t("add_mansione"), use_container_width=True):
                if nuova_mans and nuova_mans not in st.session_state.mansioni_custom:
                    st.session_state.mansioni_custom.append(nuova_mans)
                    salva_dati_locali()
                    st.rerun()

        st.write("Mansioni attive:", st.session_state.mansioni_custom)

    with tab2:
        render_tip("tip_staff")
        st.subheader("👥 Gestione Personale e Competenze (Mansioni)")
        
        with st.form("form_aggiungi_dip"):
            c_nom, c_cog = st.columns(2)
            with c_nom:
                nome_d = st.text_input("Nome Dipendente")
            with c_cog:
                cognome_d = st.text_input("Cognome Dipendente")
            
            if st.form_submit_button("➕ Aggiungi Nuovo Dipendente", use_container_width=True):
                if nome_d and cognome_d:
                     nuovo_dip = {
                         "id": str(len(st.session_state.dipendenti) + 1),
                         "nome": nome_d,
                         "cognome": cognome_d,
                         "mansioni": [st.session_state.mansioni_custom[0]] if st.session_state.mansioni_custom else ["Operatore"]
                     }
                     st.session_state.dipendenti.append(nuovo_dip)
                     salva_dati_locali()
                     st.success(f"Dipendente {nome_d} {cognome_d} aggiunto!")
                     st.rerun()
                else:
                    st.error("Inserisci nome e cognome.")

        st.markdown("---")
        st.subheader("🛠️ Tabella Interattiva con Spunte per Assegnazione Mansioni")
        
        if not st.session_state.dipendenti:
            st.info("ℹ️ Nessun dipendente inserito. Aggiungine uno sopra per abilitare la tabella con le spunte.")
        else:
            if not st.session_state.mansioni_custom:
                st.warning("⚠️ Aggiungi prima almeno una mansione nel tab 'Struttura Aziendale'.")
            else:
                righe_matrice = []
                for d in st.session_state.dipendenti:
                    riga = {
                        "ID": d.get("id"),
                        "Nome": d.get("nome"),
                        "Cognome": d.get("cognome")
                    }
                    mansioni_attuali = d.get("mansioni", [])
                    for m in st.session_state.mansioni_custom:
                        riga[m] = m in mansioni_attuali
                    righe_matrice.append(riga)
                
                df_matrice = pd.DataFrame(righe_matrice)
                
                df_modificato = st.data_editor(
                    df_matrice,
                    disabled=["ID", "Nome", "Cognome"],
                    use_container_width=True,
                    key="editor_staff_mansioni"
                )
                
                if st.button(t("save_changes"), type="primary", use_container_width=True):
                    nuova_lista_dipendenti = []
                    for index, row in df_modificato.iterrows():
                        d_id = str(row["ID"])
                        d_nome = row["Nome"]
                        d_cognome = row["Cognome"]
                        
                        mansioni_spuntate = []
                        for m in st.session_state.mansioni_custom:
                            if row[m]:
                                mansioni_spuntate.append(m)
                                
                        nuova_lista_dipendenti.append({
                            "id": d_id,
                            "nome": d_nome,
                            "cognome": d_cognome,
                            "mansioni": mansioni_spuntate
                        })
                    
                    st.session_state.dipendenti = nuova_lista_dipendenti
                    salva_dati_locali()
                    st.success("✅ Modifiche e spunte mansioni salvate con successo!")
                    st.rerun()

    with tab3:
        render_tip("tip_fabbisogno")
        st.subheader("📈 Fabbisogno Operativo per Reparto")
        if not st.session_state.reparti_custom:
            st.warning("Aggiungi prima almeno un reparto nel tab 'Struttura Aziendale'.")
        else:
            rep_sel = st.selectbox("Seleziona Reparto da configurare:", options=st.session_state.reparti_custom)
            df_fabb = get_fabbisogno_reparto_df(rep_sel)
            edited_df = st.data_editor(df_fabb, key=f"fabb_{rep_sel}", use_container_width=True)
            st.session_state.fabbisogno_per_reparto[rep_sel] = edited_df
            if st.button(t("save_changes"), use_container_width=True):
                salva_dati_locali()
                st.success("Fabbisogno salvato correttamente!")

    with tab4:
        render_tip("tip_assenze")
        st.subheader("📅 Gestione Ferie e Assenze")
        if not st.session_state.dipendenti:
            st.warning("Aggiungi prima i dipendenti nel tab 'Staff & Anagrafica'.")
        else:
            dip_nomi = [f"{d['nome']} {d['cognome']}" for d in st.session_state.dipendenti]
            giorni_sett = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
            
            with st.form("form_assenza"):
                d_scelto = st.selectbox("Dipendente", options=dip_nomi)
                g_scelto = st.selectbox("Giorno", options=giorni_sett)
                motivo = st.selectbox("Motivo", options=["Ferie", "Permesso", "Malattia"])
                if st.form_submit_button("Registra Assenza", use_container_width=True):
                    st.session_state.registro_assenze.append({"Dipendente": d_scelto, "Giorno": g_scelto, "Motivo": motivo})
                    salva_dati_locali()
                    st.success("Assenza registrata!")
                    st.rerun()

            if st.session_state.registro_assenze:
                st.write("Assenze registrate:")
                st.dataframe(pd.DataFrame(st.session_state.registro_assenze), use_container_width=True)

    with tab5:
        render_tip("tip_generatore")
        st.subheader("⚡ Generatore Intelligente Turni")
        if st.button(t("generate_btn"), type="primary", use_container_width=True):
            griglia = genera_turni_ottimizzati()
            if griglia is not None:
                st.session_state.griglia_corrente = griglia
                st.success("✅ Turni generati con successo!")
            else:
                st.error("⚠️ Impossibile generare i turni. Verifica di aver inserito dipendenti e fabbisogno.")

        if st.session_state.griglia_corrente is not None:
            st.markdown("### 📊 Griglia Turni Attuale")
            st.dataframe(st.session_state.griglia_corrente, use_container_width=True)
            
            img_bytes = genera_immagine_turni(st.session_state.griglia_corrente.reset_index())
            st.download_button(
                label="📥 Scarica Griglia Turni (PNG)",
                data=img_bytes,
                file_name="turni_shiftia.png",
                mime="image/png",
                use_container_width=True
            )

    with tab6:
        st.subheader("⚙️ Impostazioni e Archivio")
        st.write("Puoi resettare o cancellare i dati dell'azienda corrente.")
        if st.button("🗑️ Elimina Azienda Corrente", type="primary", use_container_width=True):
            az_corr = st.session_state.azienda_corrente
            elimina_azienda(az_corr)
            st.success("Azienda eliminata. Verrai reindirizzato.")
            st.rerun()

def pannello_dipendente():
    st.sidebar.title("👤 Area Dipendente")
    st.sidebar.write(f"🏢 Azienda: **{st.session_state.azienda_corrente}**")
    if st.sidebar.button(t("logout_btn"), use_container_width=True):
        st.session_state.ruolo_accesso = None
        st.session_state.dipendente_corrente = None
        st.session_state.azienda_corrente = None
        st.rerun()

    st.subheader("👋 Benvenuto nella tua Area Personale")
    if st.session_state.griglia_corrente is not None:
        st.markdown("### 📅 La tua pianificazione turni")
        st.dataframe(st.session_state.griglia_corrente, use_container_width=True)
    else:
        st.info("ℹ️ Nessun turno pubblicato al momento dal gestore.")

# ==========================================
# 7. MAIN EXECUTION BLOCK
# ==========================================
def main():
    init_session_state()
    inject_custom_css()

    if st.session_state.ruolo_accesso is None:
        schermata_landing()
    elif st.session_state.ruolo_accesso == "Gestore" and not st.session_state.get("autenticato_gestore", False):
        col_back, _ = st.columns([4, 1])
        with col_back:
            if st.button(t('back_btn')):
                st.session_state.ruolo_accesso = None
                st.rerun()
        
        st.subheader(t("login_gestore_title"))
        elenco_aziende = list(st.session_state.aziende.keys())
        if elenco_aziende:
            az_sel = st.selectbox("Seleziona Azienda:", options=elenco_aziende)
            imposta_azienda_attiva(az_sel)
            password_input = st.text_input("Password Gestore", type="password")
            if st.button(t("login_btn"), type="primary", use_container_width=True):
                st.session_state.autenticato_gestore = True
                st.success("Accesso effettuato!")
                st.rerun()
        else:
            st.info("Nessuna azienda presente. Registrane una dalla home.")
    elif st.session_state.ruolo_accesso == "Gestore" and st.session_state.get("autenticato_gestore", False):
        if not st.session_state.get("wizard_completato", False):
            render_interactive_wizard()
        else:
            pannello_gestore()
    elif st.session_state.ruolo_accesso == "Dipendente":
        pannello_dipendente()

if __name__ == "__main__":
    main()
