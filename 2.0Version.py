import json
import re
import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

st.set_page_config(page_title="Contracts", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
        :root {
            --prod: #2E7D32;  --prod2: #66BB6A;
            --conc: #212121;  --conc2: #757575;
            --maint: #1B6E3A; --maint2: #1565C0;
            --cust: #00609E;  --cust2: #00AEEF;
            --land: #8A4B12;  --land2: #DB6F20;
            --perg: #6D3F17;  --perg2: #A9744A;
            --home: #1B5E20;  --home2: #43A047;
            --arch: #616161;  --arch2: #9E9E9E;
        }
        .block-container {
            max-width: 1120px; margin: 0 auto;
            padding: 3.2rem 2rem 3rem 2rem;
        }
        /* Page banner */
        .contracts-hero {
            border-radius: 16px; padding: 1.1rem 1.6rem; margin: 0.4rem 0 1.4rem 0;
            color: #fff; background: linear-gradient(120deg, var(--home), var(--home2));
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        }
        .contracts-hero h1 { color: #fff !important; margin: 0; padding: 0; font-size: 1.65rem; }
        .hero-center { text-align: center; padding: 1.5rem 1.6rem !important; }
        .hero-center h1 { font-size: 2.9rem !important; letter-spacing: 0.01em; }
        .contracts-hero p { color: rgba(255,255,255,0.9); margin: 0.35rem 0 0 0; }
        .section-kicker {
            color: rgba(255,255,255,0.85); text-transform: uppercase; letter-spacing: 0.14em;
            font-size: 0.74rem; font-weight: 700; margin-bottom: 0.25rem;
        }
        .theme-production  { background: linear-gradient(120deg, var(--prod),  var(--prod2)); }
        .theme-concrete    { background: linear-gradient(120deg, var(--conc),  var(--conc2)); }
        .theme-maintenance { background: linear-gradient(120deg, var(--maint), var(--maint2)); }
        .theme-customs     { background: linear-gradient(120deg, var(--cust),  var(--cust2)); }
        .theme-land        { background: linear-gradient(120deg, var(--land),  var(--land2)); }
        .theme-pergolas    { background: linear-gradient(120deg, var(--perg),  var(--perg2)); }
        .theme-archived    { background: linear-gradient(120deg, var(--arch),  var(--arch2)); }

        div[data-testid="stButton"] > button { min-height: 3.15rem; border-radius: 10px; font-weight: 650; }

        /* Home page division tiles: company logo inside each button */
        [class*="st-key-tile_"] button {
            min-height: 14rem !important; width: 100%;
            background-color: #ffffff !important; background-repeat: no-repeat !important;
            background-position: center 0.9rem !important; background-size: auto 9.6rem !important;
            border: 1px solid rgba(128,128,128,0.28) !important; border-bottom-width: 8px !important;
            border-radius: 16px !important; box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            align-items: flex-end !important; padding-bottom: 0.6rem !important; color: #1f2937 !important;
            transition: transform .12s, box-shadow .12s;
        }
        [class*="st-key-tile_"] button:hover { transform: translateY(-3px); box-shadow: 0 10px 22px rgba(0,0,0,0.18); }
        [class*="st-key-tile_"] button p { font-size: 1.35rem; font-weight: 750; color: #1f2937; }
        .st-key-tile_production button  { border-bottom-color: var(--prod) !important; }
        .st-key-tile_concrete button    { border-bottom-color: var(--conc) !important; }
        .st-key-tile_maintenance button { border-bottom-color: var(--maint2) !important; }
        .st-key-tile_customs button     { border-bottom-color: var(--cust2) !important; }
        .st-key-tile_land button        { border-bottom-color: var(--land2) !important; align-items: center !important; padding-bottom: 0 !important; }
        .st-key-tile_land button p      { font-size: 1.9rem !important; }
        .st-key-tile_billing button     { border-bottom-color: #6A1B9A !important; align-items: center !important; padding-bottom: 0 !important; }
        .st-key-tile_billing button p   { font-size: 1.9rem !important; }
        .theme-billing     { background: linear-gradient(120deg, #4A148C, #8E24AA); }
        .st-key-tile_pergolas button    { border-bottom-color: var(--perg) !important; }
        .tile-note { text-align: center; opacity: 0.7; font-size: 0.95rem; margin: -0.3rem 0 1.3rem 0; }

        /* Builder buttons: coloured edge per division */
        [class*="st-key-grid_"] div[data-testid="stButton"] > button {
            min-height: 7.4rem !important; background-color: #ffffff !important; color: #1f2937 !important;
            border: 1px solid rgba(128,128,128,0.28); border-left-width: 8px; border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            background-repeat: no-repeat !important; background-position: center 0.75rem !important;
            background-size: auto 3.3rem !important;
        }
        [class*="st-key-grid_"] [class*="st-key-builder_"]:not(.st-key-builder_production_other_builders):not(.st-key-builder_concrete_other_builders) button {
            align-items: flex-end !important; padding-bottom: 0.55rem !important;
        }
        [class*="st-key-grid_"] div[data-testid="stButton"] > button:hover { box-shadow: 0 6px 14px rgba(0,0,0,0.18); transform: translateY(-2px); }
        [class*="st-key-grid_"] div[data-testid="stButton"] > button p { color: #1f2937 !important; }
        .st-key-grid_production div[data-testid="stButton"] > button { border-left-color: var(--prod); }
        .st-key-grid_concrete div[data-testid="stButton"] > button   { border-left-color: var(--conc); }
        .builder-count { text-align: center; opacity: 0.7; font-size: 0.9rem; margin: 0.25rem 0 1rem 0; }
        [class*="st-key-grid_"] div[data-testid="stButton"] > button p { font-size: 1.3rem; font-weight: 750; }

        /* Back / Home buttons: big and easy to spot */
        [class*="st-key-back"] button, [class*="st-key-homebtn"] button {
            min-height: 3.1rem !important; padding: 0.3rem 1.5rem !important; border-radius: 999px !important;
            background: #ffffff !important; border: 3px solid #C62828 !important;
            color: #111111 !important; box-shadow: 0 2px 8px rgba(198,40,40,0.25) !important;
        }
        [class*="st-key-back"] button p, [class*="st-key-homebtn"] button p {
            font-size: 1.15rem; font-weight: 900 !important; color: #111111 !important;
        }
        [class*="st-key-back"] button:hover, [class*="st-key-homebtn"] button:hover {
            background: #C62828 !important; border-color: #C62828 !important;
        }
        [class*="st-key-back"] button:hover p, [class*="st-key-homebtn"] button:hover p { color: #ffffff !important; }
        [class*="st-key-refresh"] button { min-height: 2.3rem !important; font-size: 0.85rem; color: #4b5563; }

        /* Search box on home page */
        .st-key-home_search_box {
            background: rgba(128,128,128,0.07); border: 1px solid rgba(128,128,128,0.28); border-radius: 14px;
            padding: 0.9rem 1.1rem 0.6rem 1.1rem; margin-bottom: 1.6rem;
        }
        /* Search results: one row per community, coloured edge = division */
        [class*="st-key-hit_"] button {
            min-height: 2.6rem !important; justify-content: flex-start; text-align: left;
            background: transparent; border: 1px solid rgba(128,128,128,0.25); border-left-width: 6px;
        }
        [class*="st-key-hit_"] button p { font-size: 1rem; text-align: left; }
        [class*="st-key-hit_"] button > div { justify-content: flex-start; width: 100%; }
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {
            border-color: #2E7D32 !important;
        }
        /* Alpha green for main action buttons (works with light or dark system theme) */
        a[data-testid="stBaseLinkButton-primary"] {
            background-color: #2E7D32 !important; border-color: #2E7D32 !important; color: #fff !important;
        }
        a[data-testid="stBaseLinkButton-primary"]:hover { background-color: #1B5E20 !important; }
        @media (prefers-color-scheme: dark) {
            [class*="st-key-back"] button, [class*="st-key-homebtn"] button { border-color: #EF5350 !important; }
        }
        button[kind="primary"], button[data-testid="stBaseButton-primary"] {
            background-color: #2E7D32 !important; border-color: #2E7D32 !important; color: #fff !important;
        }
        button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
            background-color: #1B5E20 !important; border-color: #1B5E20 !important;
        }
        [class*="st-key-hit_production"] button { border-left-color: var(--prod); }
        [class*="st-key-hit_concrete"] button   { border-left-color: var(--conc); }
        [class*="st-key-hit_pergolas"] button   { border-left-color: var(--perg); }
        [class*="st-key-hit_customs"] button    { border-left-color: var(--cust2); }
        [class*="st-key-hit_land"] button       { border-left-color: var(--land2); }

        /* Contract document viewer (Customs / Commercial) */
        .doc-card { border: 1px solid rgba(128,128,128,0.28); border-left: 8px solid var(--cust2); border-radius: 14px;
                    padding: 0.8rem 1.2rem; margin: 0.6rem 0 0.9rem 0; background: rgba(128,128,128,0.05); }
        .doc-card.land { border-left-color: var(--land2); }
        .doc-card.po { border-left-color: #8E24AA; }
        .doc-card.po .doc-pill { background: rgba(142,36,170,0.13); color: #4A148C; }
        [class*="st-key-hit_po"] button         { border-left-color: #8E24AA; }
        .doc-card .doc-title { font-size: 1.08rem; font-weight: 700; }
        .doc-card .doc-meta { opacity: 0.7; font-size: 0.9rem; margin-top: 0.15rem; }
        .doc-pill { display: inline-block; padding: 0.1rem 0.6rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700;
                    background: rgba(0,174,239,0.15); color: #00609E; margin-right: 0.4rem; }
        .doc-card.land .doc-pill { background: rgba(219,111,32,0.15); color: #8A4B12; }

        .builder-spacer { height: 0.7rem; }
        .archive-note { text-align: center; opacity: 0.7; font-size: 0.78rem; margin: 0.2rem 0 0.5rem 0; }
        .app-footer { text-align: center; opacity: 0.6; font-size: 0.85rem; padding-top: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent

# Division logos (from alphalandscapeslv.com) shown on the home-page buttons.
TILE_LOGOS = {
    "production": "logo_production.png",
    "concrete": "logo_concrete.png",
    "pergolas": "logo_patio.png",
    "maintenance": "logo_maintenance.png",
    "customs": "logo_customs.png",
}


@st.cache_data
def logo_data_uri(filename):
    import base64
    path = BASE_DIR / "assets" / filename
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def inject_tile_logo_css():
    rules = []
    for key, filename in TILE_LOGOS.items():
        uri = logo_data_uri(filename)
        if uri:
            rules.append(
                f'.st-key-tile_{key} button {{ background-image: url("{uri}") !important; }}'
            )
    st.markdown("<style>" + "\n".join(rules) + "</style>", unsafe_allow_html=True)


# Builder logos on the Production / Concrete builder buttons (Other Builders has none).
BUILDER_LOGOS = [
    "pulte", "woodside", "richmond", "taylor_morrison",
    "century_communities", "kb_homes", "tri_pointe",
]


def inject_builder_logo_css(division):
    rules = []
    for slug in BUILDER_LOGOS:
        uri = logo_data_uri(f"builder_{slug}.png")
        if uri:
            rules.append(
                f'.st-key-builder_{division}_{slug} button {{ background-image: url("{uri}") !important; }}'
            )
    st.markdown("<style>" + "\n".join(rules) + "</style>", unsafe_allow_html=True)


REQUIRED_COLUMNS = ["Community", "Series", "Scar.Date", "Plan", "Work Type", "Amount"]
NOTE_COLUMN = "Note"

CONTRACTS_SHARED_URL = (
    "https://alphalandscapeslv-my.sharepoint.com/:f:/p/alejandroe/"
    "IgBa5H5bojr_RbSnca96B7jBAUpkCrpcHsdISsNM7eXFoyU?e=JWc08Z"
)
CONTRACT_FOLDERS_FILE = "contract_folders.json"

CUSTOMS_SHARED_URL = (
    "https://alphalandscapeslv-my.sharepoint.com/:f:/p/alejandroe/"
    "IgBl0A5r1SFsTrHGb8XcYPOnAYLGQ-S3cihnTjd1c-dNwDI?e=jKYv23"
)

MAINTENANCE_SHARED_URL = (
    "https://alphalandscapeslv-my.sharepoint.com/:f:/p/alejandroe/"
    "IgCfnlzeFH4lQYHCdShYOVTEATgE7ucG-oAw_QGeVECOLhw?e=e4piss"
)
MAINTENANCE_REPO = "Maintenance-Recurring"

MONTH_NUMBER = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


BUILDER_ORDER = [
    "Pulte",
    "Woodside",
    "Richmond",
    "Taylor Morrison",
    "Century Communities",
    "KB Homes",
    "Tri Pointe of Nevada",
    "Other Builders",
]

BUILDER_SLUGS = {
    "Pulte": "pulte",
    "Woodside": "woodside",
    "Richmond": "richmond",
    "Taylor Morrison": "taylor_morrison",
    "Century Communities": "century_communities",
    "KB Homes": "kb_homes",
    "Tri Pointe of Nevada": "tri_pointe",
    "Other Builders": "other_builders",
}

BUILDER_FILES = {
    "Pulte": "PulteContracts1.xlsx",
    "Woodside": "WoodsideContracts1.xlsx",
    "Richmond": "RichmondContracts1.xlsx",
    "Taylor Morrison": "TaylorMorrisonContracts1.xlsx",
    "Century Communities": "CenturyCommunitiesContracts1.xlsx",
    "KB Homes": "KBHomesContracts1.xlsx",
    "Tri Pointe of Nevada": "TriPointeContracts1.xlsx",
    # AMH Development, Blue Heron, Pinnacle Homes, ... (Community = "Builder - Community")
    "Other Builders": "OtherBuildersContracts1.xlsx",
}

ACTIVE_BUILDERS = set(BUILDER_FILES)

# One shared workbook for patio-cover / pergola (Alumawood) pricing from every
# builder. Community names are "Builder - Community" (e.g. "KB - Caspian Bay 35s").
PERGOLAS_FILE = "PergolasContracts1.xlsx"

ARCHIVED_COMMUNITIES = {
    ("Pulte", "production"): {
        "Aldervista",
        "Ashcroft",
        "Blacktail",
        "Carmel Cliff",
        "Jones.Crossing",
        "Liberty.Silvercourt",
        "Linmar.Ranch",
        "Monument@Reverence",
        "Southbrooks",
        "Talvona",
        "Valridge",
        "Paldona@Russell",
        "Paldona@Buffalo",
        "Paldona@WarmSprings",
        "RC.Estates",
        "Hayford@Polaris",
        "Daylight@Cameron",
        "Liberty",
        "Liberty.CT.8",
        "Luxury@Russell",
        "Luxury@Warm Springs",
        "Incline",
        "Cordora",
    },
    ("Pulte", "concrete"): set(),
    ("Woodside", "production"): {
        # Only warranty work on SupplyPro in 2026.
        "Estrella at Sunstone",
        "Luna at Sunstone",
    },
    ("Woodside", "concrete"): set(),
}

EXPECTED_PULTE_CONCRETE = {
    "Tenaya Springs @ Landberg - Concrete",
    "Tenaya Springs @ Lone Mesa - Concrete",
    "Tenaya Springs @ Patrick - Concrete",
}


GITHUB_OWNER = "TapatioSpice"
CONTRACT_REPO = "Contract-Files"
CONTRACT_BRANCHES = ("main", "master")


def contract_file_candidates(filename):
    """Local fallbacks for desktop/local testing.

    Streamlit Community Cloud clones only the Alpha-Contracts repository, so a
    separate Contract-Files repository is NOT available as a sibling folder.
    These paths are therefore only fallbacks for local testing.
    """
    return [
        BASE_DIR / filename,
        BASE_DIR / "Contract-Files" / filename,
        BASE_DIR.parent / "Contract-Files" / filename,
    ]


def github_token():
    """Optional token for a private Contract-Files repository."""
    try:
        return st.secrets.get("GITHUB_TOKEN")
    except Exception:
        return None


def download_contract_file(filename):
    """Download one workbook from the separate Contract-Files GitHub repo.

    Public repos work without a token. If Contract-Files is private, add a
    GITHUB_TOKEN secret in Streamlit with read access to that repository.
    """
    token = github_token()
    errors = []

    for branch in CONTRACT_BRANCHES:
        url = (
            f"https://raw.githubusercontent.com/{GITHUB_OWNER}/"
            f"{CONTRACT_REPO}/{branch}/{filename}"
        )
        headers = {"User-Agent": "Alpha-Contracts-Streamlit"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=20) as response:
                return BytesIO(response.read()), url
        except HTTPError as exc:
            errors.append(f"{branch}: HTTP {exc.code}")
        except URLError as exc:
            errors.append(f"{branch}: {exc.reason}")
        except Exception as exc:
            errors.append(f"{branch}: {exc}")

    raise FileNotFoundError(
        f"Could not download {filename} from {GITHUB_OWNER}/{CONTRACT_REPO}. "
        + " | ".join(errors)
    )


@st.cache_data(ttl=300)
def load_builder_data(builder_name):
    return load_contract_workbook(BUILDER_FILES[builder_name], builder_name)


@st.cache_data(ttl=300)
def load_contract_workbook(filename, builder_name=""):

    # Local file first (useful when testing on your computer).
    local_path = next((path for path in contract_file_candidates(filename) if path.exists()), None)

    try:
        if local_path is not None:
            data = pd.read_excel(local_path)
        else:
            remote_file, remote_url = download_contract_file(filename)
            data = pd.read_excel(remote_file)
    except Exception as exc:
        st.error(
            f"Unable to load {filename} from the Contract-Files GitHub repository. "
            f"Make sure the file is in the root of TapatioSpice/Contract-Files and is named exactly {filename}."
        )
        st.caption(
            "If Contract-Files is private, add GITHUB_TOKEN in Streamlit → App settings → Secrets "
            "with read access to that repository."
        )
        st.code(str(exc))
        st.stop()

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        st.error("The contract file is missing required column(s): " + ", ".join(missing))
        st.stop()

    # Optional "Note" column (e.g. "Price reduced from contract approved by Tony").
    # It is shown next to the contract date and above the pricing table.
    has_note = NOTE_COLUMN in data.columns
    data = data[REQUIRED_COLUMNS + ([NOTE_COLUMN] if has_note else [])].copy()
    if has_note:
        data[NOTE_COLUMN] = data[NOTE_COLUMN].fillna("").astype(str).str.strip()
    else:
        data[NOTE_COLUMN] = ""

    for column in ["Community", "Plan", "Work Type"]:
        data[column] = data[column].astype(str).str.strip()

    data["Scar.Date"] = pd.to_datetime(data["Scar.Date"], errors="coerce")
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")

    data = data.dropna(
        subset=["Community", "Series", "Scar.Date", "Plan", "Work Type", "Amount"]
    )

    # Ironstone DMT submittal plan-name safeguard.
    # This also fixes display if Streamlit briefly reads an older cached copy
    # of PulteContracts1.xlsx that still says "DMT Plan 1/2/3".
    if builder_name == "Pulte":
        ironstone_mask = (
            data["Community"].eq("Evercrest at Ironstone")
            & data["Series"].astype(str).str.strip().eq("5500")
            & data["Scar.Date"].dt.normalize().eq(pd.Timestamp("2026-08-31"))
        )
        ironstone_plan_names = {
            "DMT Plan 1": "5526-7 - Genoa",
            "DMT Plan 2": "5527-7 - Catalina",
            "DMT Plan 3": "5528-7 - Cesena",
        }
        data.loc[ironstone_mask, "Plan"] = (
            data.loc[ironstone_mask, "Plan"]
            .replace(ironstone_plan_names)
        )

    return data


def concrete_mask(data):
    return data["Community"].astype(str).str.strip().str.lower().str.endswith(" - concrete")


def get_division_data(data, builder_name, division, archived=False):
    mask = concrete_mask(data)
    division_data = data[mask].copy() if division == "concrete" else data[~mask].copy()
    archive_set = ARCHIVED_COMMUNITIES.get((builder_name, division), set())

    if archived:
        return division_data[division_data["Community"].isin(archive_set)].copy()
    return division_data[~division_data["Community"].isin(archive_set)].copy()


def filter_data(data, community, series, scar_date):
    selected_date = pd.Timestamp(scar_date).normalize()
    return data[
        (data["Community"] == community)
        & (data["Series"] == series)
        & (data["Scar.Date"].dt.normalize() == selected_date)
    ].copy()


def work_type_priority(value):
    value = str(value)
    if value == "Foundation": return 0
    if value.startswith("Foundation-"): return 1
    if value.startswith("FND-"): return 2

    # Century Communities patio-cover rows are CONCRETE options.
    if value.startswith("CP"):
        return 3

    # Union Village / similar concrete drop-garage pricing.
    drop_order = {
        'Drop Garage 7"-12"': 10,
        'Cut Pad 7"-12"': 11,
        'Haul Off 7"-12"': 12,
        'Drop Garage 13"-18"': 13,
        'Cut Pad 13"-18"': 14,
        'Haul Off 13"-18"': 15,
        'Drop Garage 19"-24"': 16,
        'Cut Pad 19"-24"': 17,
        'Haul Off 19"-24"': 18,
    }
    if value in drop_order:
        return drop_order[value]
    if value == "Haul Off": return 19
    if value == "RG": return 20
    if value.startswith("RG-"): return 21
    if value == "RG2": return 22
    # Century Communities unit-price codes (Rough Grade / Final Grade /
    # Irrigation / Landscaping) so they read in job order.
    if value.startswith("GR0000"): return 23
    if value == "FG2": return 30
    if value == "FG": return 31
    if value.startswith("GF0000"): return 32
    if value == "LS": return 40
    if value == "Landscape": return 40
    if value.startswith("LSO-"): return 41
    if value.startswith("LI0000"): return 42
    if value.startswith("LL"): return 43
    if value in ("Pavers", "PV"): return 50
    if value.startswith("Pavers-"): return 51
    if value.startswith("PVO-"): return 52
    return 100


def build_contract_table(data):
    working = data.copy()
    working["Amount"] = working["Amount"].round(2)

    table_data = pd.pivot_table(
        working,
        values="Amount",
        index="Work Type",
        columns="Plan",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    table_data["_priority"] = table_data["Work Type"].map(work_type_priority)
    table_data = table_data.sort_values(
        by=["_priority", "Work Type"], kind="stable"
    ).drop(columns="_priority")

    formatted = table_data.copy()
    for column in formatted.columns:
        if column != "Work Type":
            formatted[column] = formatted[column].map(lambda value: f"{value:,.2f}")
    return formatted


def sort_display_values(values):
    return sorted(values, key=lambda value: str(value).lower())




def github_api_request(url):
    """Read JSON from GitHub, using the optional existing token when available."""
    headers = {
        "User-Agent": "Alpha-Contracts-Streamlit",
        "Accept": "application/vnd.github+json",
    }
    token = github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def maintenance_file_sort_key(item):
    """Sort monthly recurring files chronologically by month name."""
    name = str(item.get("name", "")).lower()
    month = 0
    for month_name, month_number in MONTH_NUMBER.items():
        if month_name in name:
            month = month_number
            break

    # If a year is included in a future filename, use it.
    year = pd.Timestamp.today().year
    for token in name.replace("-", " ").replace("_", " ").split():
        if token.isdigit() and len(token) == 4 and token.startswith("20"):
            year = int(token)
            break

    return (year, month, name)


@st.cache_data(ttl=300)
def list_maintenance_workbooks():
    """List recurring-maintenance Excel files directly from GitHub."""
    errors = []

    for branch in CONTRACT_BRANCHES:
        url = (
            f"https://api.github.com/repos/{GITHUB_OWNER}/"
            f"{MAINTENANCE_REPO}/contents?ref={branch}"
        )
        try:
            items = github_api_request(url)
            if not isinstance(items, list):
                continue

            files = [
                item
                for item in items
                if str(item.get("name", "")).lower().endswith((".xlsx", ".xls"))
                and "recurring" in str(item.get("name", "")).lower()
                and item.get("download_url")
            ]

            files.sort(key=maintenance_file_sort_key, reverse=True)
            if files:
                return files
        except Exception as exc:
            errors.append(f"{branch}: {exc}")

    raise FileNotFoundError(
        f"Could not find recurring workbooks in {GITHUB_OWNER}/{MAINTENANCE_REPO}. "
        + " | ".join(errors)
    )


@st.cache_data(ttl=300)
def load_maintenance_workbook(download_url, filename):
    """Download and clean one monthly recurring-maintenance workbook."""
    headers = {"User-Agent": "Alpha-Contracts-Streamlit"}
    token = github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(download_url, headers=headers)
    with urlopen(request, timeout=25) as response:
        workbook_bytes = BytesIO(response.read())

    raw = pd.read_excel(workbook_bytes, header=None)

    header_row = None
    for idx in range(min(len(raw), 15)):
        first_value = str(raw.iloc[idx, 0]).strip().lower()
        if first_value == "client name":
            header_row = idx
            break

    if header_row is None:
        raise ValueError(f"Could not find the 'Client name' header in {filename}.")

    records = []
    source_total = None

    for idx in range(header_row + 1, len(raw)):
        row = raw.iloc[idx]

        client = row.iloc[0] if len(row) > 0 else None
        property_name = row.iloc[1] if len(row) > 1 else None
        frequency = row.iloc[2] if len(row) > 2 else None
        amount = row.iloc[3] if len(row) > 3 else None
        note = row.iloc[4] if len(row) > 4 else None

        frequency_text = "" if pd.isna(frequency) else str(frequency).strip()
        client_text = "" if pd.isna(client) else str(client).strip()

        if frequency_text.lower() == "total":
            source_total = pd.to_numeric(amount, errors="coerce")
            break

        if not client_text:
            continue

        numeric_amount = pd.to_numeric(amount, errors="coerce")
        if pd.isna(numeric_amount):
            continue

        records.append(
            {
                "Client": client_text,
                "Property": "" if pd.isna(property_name) else str(property_name).strip(),
                "Frequency": frequency_text,
                "Monthly Amount": float(numeric_amount),
                "Note": "" if pd.isna(note) else str(note).strip(),
            }
        )

    data = pd.DataFrame(records)
    if data.empty:
        return data, 0.0, source_total

    calculated_total = float(data["Monthly Amount"].sum())
    return data, calculated_total, source_total


def maintenance_month_label(filename):
    name = Path(filename).stem
    return name.replace("_", " ").strip()



def set_page(page_name):
    """Remember the page in the web address (?page=...) so the browser's
    back / forward arrows move between app pages instead of leaving the app."""
    st.session_state["contracts_page"] = page_name
    st.query_params["page"] = page_name


def go_to_page(page_name):
    set_page(page_name)
    st.rerun()



DMT_CONTRACT_DATE_NOTES = {
    ("Hayford", "01/05/2026"): "Based off DMT submittal",
    ("Evercrest at Ironstone", "08/31/2026"): "Based off DMT submittal",
}


def workbook_notes(rows):
    """Unique non-blank notes from the workbook's optional Note column."""
    if NOTE_COLUMN not in rows.columns:
        return []
    notes = []
    for note in rows[NOTE_COLUMN].dropna().astype(str).str.strip():
        if note and note.lower() != "nan" and note not in notes:
            notes.append(note)
    return notes


def contract_date_note(community, value):
    date_text = pd.Timestamp(value).strftime("%m/%d/%Y")
    return DMT_CONTRACT_DATE_NOTES.get((str(community), date_text))



@st.cache_data(ttl=300)
def load_contract_folders():
    """Map of 'Builder|Community' -> OneDrive folder holding that community's contract PDFs.

    Lives in Contract-Files as contract_folders.json so it can be edited without
    touching this code. Missing or unreadable file = just show the main folder link.
    """
    try:
        local_path = next(
            (path for path in contract_file_candidates(CONTRACT_FOLDERS_FILE) if path.exists()),
            None,
        )
        if local_path is not None:
            return json.loads(local_path.read_text(encoding="utf-8"))
        remote_file, _ = download_contract_file(CONTRACT_FOLDERS_FILE)
        return json.loads(remote_file.read().decode("utf-8"))
    except Exception:
        return {}


def render_contract_pdf_link(builder_name, community, key, series=None):
    """Button that opens this community's own Contract folder in OneDrive.

    contract_folders.json keys are "Builder|Community" and, where one app
    community covers several OneDrive folders (e.g. Pulte Aries 2500/3000/...),
    "Builder|Community|Series". The series key wins when it exists.
    """
    config = load_contract_folders()
    folders = config.get("folders", {})
    entry = {}
    if series is not None and str(series).strip():
        entry = folders.get(f"{builder_name}|{community}|{series}", {})
    if not entry:
        entry = folders.get(f"{builder_name}|{community}", {})
    url = entry.get("url") or config.get("shared_folder_url") or CONTRACTS_SHARED_URL
    path = entry.get("path", "")

    cols = st.columns([1.4, 3])
    with cols[0]:
        st.link_button("📄 Contract PDFs", url, use_container_width=True)
    with cols[1]:
        crumbs = " › ".join(["CONTRACTS"] + [p for p in path.split("/") if p]) if path else ""
        if entry.get("url") and entry.get("level", "community") == "community":
            st.caption(f"Opens **{crumbs}**")
        elif entry.get("url"):
            st.caption(f"No contract PDF filed for this community yet — opens **{crumbs}**")
        elif path:
            st.caption(f"Open the folder, then go to: **{crumbs}**")
        else:
            st.caption("No contract PDF filed for this community yet — opens the shared CONTRACTS folder.")


def render_contract_browser(data, key_prefix, builder_name=""):
    if data.empty:
        st.info("No contracts loaded.")
        if builder_name:
            render_contract_pdf_link(builder_name, "", f"{key_prefix}_pdfs")
        return

    communities = sort_display_values(data["Community"].dropna().unique())
    pick_cols = st.columns([1.5, 1, 1.5], gap="medium")
    with pick_cols[0]:
        selected_community = st.selectbox(
            "1. Select Community",
            communities,
            key=f"{key_prefix}_community",
        )

    series_options = sort_display_values(
        data.loc[data["Community"] == selected_community, "Series"].dropna().unique()
    )
    with pick_cols[1]:
        selected_series = st.selectbox(
            "2. Select Series",
            series_options,
            key=f"{key_prefix}_series",
        )

    date_data = data[
        (data["Community"] == selected_community)
        & (data["Series"] == selected_series)
    ]
    scar_dates = sorted(
        date_data["Scar.Date"].dropna().dt.normalize().unique(),
        reverse=True,
    )

    selected_scar_date = None
    if scar_dates:
        newest_date = pd.Timestamp(scar_dates[0]).normalize()

        def date_label(value):
            current = pd.Timestamp(value).normalize()
            label = current.strftime("%m/%d/%Y")
            status = "Current / Newest" if current == newest_date else "Historical"
            notes = [contract_date_note(selected_community, current)]
            notes += workbook_notes(date_data[date_data["Scar.Date"].dt.normalize() == current])
            notes = [note for note in notes if note]
            return f"{label} — {status} • {' • '.join(notes)}" if notes else f"{label} — {status}"

        with pick_cols[2]:
            selected_scar_date = st.selectbox(
                "3. Select Scar / Contract Effective Date",
                scar_dates,
                index=0,
                format_func=date_label,
                key=f"{key_prefix}_scar_date",
            )

    if builder_name:
        render_contract_pdf_link(builder_name, selected_community, f"{key_prefix}_pdfs", selected_series)

    if st.button("Create Table", type="primary", key=f"{key_prefix}_create"):
        if selected_scar_date is None:
            st.warning("Please select a contract date.")
            return

        selected = filter_data(
            data,
            selected_community,
            selected_series,
            selected_scar_date,
        )
        if selected.empty:
            st.warning("No pricing was found for the selected contract.")
            return

        date_text = pd.Timestamp(selected_scar_date).strftime("%m/%d/%Y")
        st.subheader(f"{selected_community} — {selected_series} — {date_text}")
        for note in workbook_notes(selected):
            st.info(note)
        st.dataframe(
            build_contract_table(selected),
            hide_index=True,
            use_container_width=True,
        )



def show_maintenance_home():
    if st.button("⬅  Back to Home", key="back_home_maintenance"):
        go_to_page("home")

    st.markdown(
        """
        <div class="contracts-hero theme-maintenance">
            <div class="section-kicker">Maintenance</div>
            <h1>Maintenance</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Most important / most-used option first and full width.
    if st.button(
        "Expected Monthly Revenue",
        type="primary",
        key="open_maintenance_revenue",
        use_container_width=True,
    ):
        go_to_page("maintenance_revenue")

    st.markdown('<div class="builder-spacer"></div>', unsafe_allow_html=True)

    st.link_button(
        "Maintenance Contracts",
        MAINTENANCE_SHARED_URL,
        use_container_width=True,
    )


def show_maintenance_revenue():
    if st.button("⬅  Back to Maintenance", key="back_maintenance_revenue"):
        go_to_page("maintenance_home")

    left, right = st.columns([4, 1])
    with right:
        if st.button(
            "Refresh Data",
            key="refresh_maintenance_revenue",
            use_container_width=True,
        ):
            st.cache_data.clear()
            st.rerun()

    st.markdown(
        """
        <div class="contracts-hero theme-maintenance">
            <div class="section-kicker">Maintenance</div>
            <h1>Expected Monthly Revenue</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        files = list_maintenance_workbooks()
    except Exception as exc:
        st.error(
            f"Unable to load monthly files from {GITHUB_OWNER}/{MAINTENANCE_REPO}."
        )
        st.code(str(exc))
        return

    if not files:
        st.info("No recurring maintenance workbooks were found.")
        return

    labels = [maintenance_month_label(item["name"]) for item in files]
    file_by_label = {maintenance_month_label(item["name"]): item for item in files}

    selected_label = st.selectbox(
        "Month",
        labels,
        index=0,
        key="maintenance_month",
    )
    selected_file = file_by_label[selected_label]

    try:
        data, calculated_total, source_total = load_maintenance_workbook(
            selected_file["download_url"],
            selected_file["name"],
        )
    except Exception as exc:
        st.error(f"Unable to read {selected_file['name']}.")
        st.code(str(exc))
        return

    if data.empty:
        st.info("No active recurring revenue lines were found in this workbook.")
        return

    metric_cols = st.columns([1.4, 1, 1], gap="large")
    with metric_cols[0]:
        st.metric("Expected Revenue", f"${calculated_total:,.0f}")
    with metric_cols[1]:
        st.metric("Recurring Lines", f"{len(data):,}")
    with metric_cols[2]:
        st.metric(
            "Average / Line",
            f"${(calculated_total / len(data)):,.0f}" if len(data) else "$0",
        )

    if source_total is not None and not pd.isna(source_total):
        if abs(float(source_total) - calculated_total) > 0.01:
            st.warning(
                f"The workbook total is ${float(source_total):,.2f}, while the "
                f"active-line calculation is ${calculated_total:,.2f}."
            )

    st.markdown("<br>", unsafe_allow_html=True)

    search_col, sort_col = st.columns([2.3, 1], gap="large")
    with search_col:
        search_text = st.text_input(
            "Search Client",
            placeholder="Type a client name...",
            key="maintenance_client_search",
        ).strip()

    with sort_col:
        sort_choice = st.selectbox(
            "Sort",
            ["Client A-Z", "Amount High → Low", "Amount Low → High"],
            key="maintenance_sort",
        )

    filtered = data.copy()

    if search_text:
        needle = search_text.lower()
        filtered = filtered[
            filtered["Client"].str.lower().str.contains(needle, regex=False, na=False)
            | filtered["Property"].str.lower().str.contains(needle, regex=False, na=False)
        ]

    if sort_choice == "Amount High → Low":
        filtered = filtered.sort_values(
            ["Monthly Amount", "Client"],
            ascending=[False, True],
            kind="stable",
        )
    elif sort_choice == "Amount Low → High":
        filtered = filtered.sort_values(
            ["Monthly Amount", "Client"],
            ascending=[True, True],
            kind="stable",
        )
    else:
        filtered = filtered.sort_values(
            "Client",
            key=lambda s: s.str.lower(),
            kind="stable",
        )

    st.caption(f"{len(filtered):,} result(s)")

    display = filtered[["Client", "Monthly Amount", "Frequency"]].copy()

    st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
        height=min(650, max(190, 37 * (len(display) + 1))),
        column_config={
            "Client": st.column_config.TextColumn("Client", width="large"),
            "Monthly Amount": st.column_config.NumberColumn(
                "Expected Revenue",
                format="$%.2f",
            ),
            "Frequency": st.column_config.TextColumn("Frequency", width="large"),
        },
    )

    st.caption(
        f"Source: {selected_file['name']} • "
        f"{GITHUB_OWNER}/{MAINTENANCE_REPO}"
    )


CUSTOMS_REPO = "Customs_Contracts"
LAND_REPO = "Land_Contracts"
DOC_REPO_BRANCH = "main"
LAND_GROUP_NAMES = {"_Builder to confirm": "Builder to confirm"}


def private_repo_bytes(repo, path):
    """Read one file from a private TapatioSpice repo (Customs_Contracts / Land_Contracts).

    Streamlit Cloud needs a GITHUB_TOKEN secret with read access to the repo.
    A sibling folder with the repo checked out is used first (local testing).
    """
    for base in (BASE_DIR / repo, BASE_DIR.parent / repo, BASE_DIR.parent / repo.lower()):
        local = base / path
        if local.is_file():
            return local.read_bytes()
    url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{repo}/contents/"
        f"{quote(path)}?ref={DOC_REPO_BRANCH}"
    )
    headers = {"User-Agent": "Alpha-Contracts-Streamlit", "Accept": "application/vnd.github.raw"}
    token = github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=60) as response:
        return response.read()


@st.cache_data(ttl=300, show_spinner=False)
def load_document_index(repo, index_file="index.json"):
    """Returns (documents, error). Each document: group, job, lot, title, type, date, path, size_kb."""
    try:
        data = json.loads(private_repo_bytes(repo, index_file).decode("utf-8"))
        return data.get("documents", []), ""
    except HTTPError as exc:
        if exc.code in (401, 403, 404):
            return [], "no_access"
        return [], f"HTTP {exc.code}"
    except Exception as exc:  # network etc.
        return [], str(exc)


@st.cache_data(ttl=3600, max_entries=40, show_spinner=False)
def load_document_pdf(repo, path):
    return private_repo_bytes(repo, path)


def doc_group_label(group):
    return LAND_GROUP_NAMES.get(group, group)


def render_document_access_help(repo, error):
    if error == "no_access":
        st.warning(
            f"The app can't read the private **{repo}** repository yet. "
            "Add a GitHub token in Streamlit: app **Settings → Secrets** → "
            '`GITHUB_TOKEN = "github_pat_..."` (read-only *Contents* access to '
            "Customs_Contracts and Land_Contracts), then reboot the app."
        )
    else:
        st.error(f"Could not load the {repo} documents: {error}")


def render_document_browser(repo, key, theme, two_level, group_label="Builder", job_label="Community"):
    """Pick a job (and builder), then a document; the PDF shows right on the page."""
    docs, error = load_document_index(repo)
    if error:
        render_document_access_help(repo, error)
        return
    if not docs:
        st.info("No contracts loaded yet.")
        return

    def job_name(d):
        return d["job"] if not two_level and d["group"] == "Custom Homes" else (
            d["job"] if two_level else f'{d["group"]} › {d["job"]}'
        )

    groups = sorted({d["group"] for d in docs}, key=lambda g: (g.startswith("_"), g.lower()))
    pick_cols = st.columns([1.2, 1.6] if two_level else [1.5, 2], gap="medium")
    if two_level:
        with pick_cols[0]:
            group = st.selectbox(f"1. Select {group_label}", groups, format_func=doc_group_label, key=f"{key}_group")
        pool = [d for d in docs if d["group"] == group]
        jobs = sort_display_values(sorted({d["job"] for d in pool}))
        with pick_cols[1]:
            job = st.selectbox(f"2. Select {job_label}", jobs, key=f"{key}_job")
        job_docs = [d for d in pool if d["job"] == job]
        step = 3
    else:
        jobs = sorted({job_name(d) for d in docs}, key=lambda j: j.lower())
        with pick_cols[0]:
            job = st.selectbox(f"1. Select {job_label}", jobs, key=f"{key}_job",
                               help="Type to search by customer or builder name")
        job_docs = [d for d in docs if job_name(d) == job]
        step = 2

    type_order = {"Contract": 0, "Proposal": 1, "Change Order": 2, "Purchase Order": 3, "Payment Schedule": 4}
    job_docs.sort(key=lambda d: d.get("date", ""), reverse=True)  # newest first within each type
    job_docs.sort(key=lambda d: (d.get("lot", ""), type_order.get(d["type"], 9)))

    def clean_title(title):
        return re.sub(r"^\d{4}-\d{2}-\d{2}\s*-\s*", "", title)

    def doc_label(i):
        d = job_docs[i]
        lot = f'{d["lot"]} · ' if d.get("lot") else ""
        date = f' · {pd.Timestamp(d["date"]).strftime("%m/%d/%Y")}' if d.get("date") else ""
        return f'{lot}{d["type"]} — {clean_title(d["title"])}{date}'

    target = pick_cols[1] if not two_level else st.container()
    with target:
        pick = st.selectbox(f"{step}. Select Document", list(range(len(job_docs))), format_func=doc_label,
                            key=f"{key}_doc_{job}")
    st.caption(f'{len(job_docs)} document{"s" if len(job_docs) != 1 else ""} for **{job}**')

    doc = job_docs[pick]
    try:
        with st.spinner("Loading PDF…"):
            pdf = load_document_pdf(repo, doc["path"])
    except Exception as exc:
        st.error(f"Could not open this PDF: {exc}")
        return

    date = pd.Timestamp(doc["date"]).strftime("%m/%d/%Y") if doc.get("date") else ""
    meta = " · ".join(x for x in [doc_group_label(doc["group"]), doc["job"], doc.get("lot", ""), date,
                                  f'{int(doc.get("size_kb", 0)):,} KB'] if x)
    st.markdown(
        f'<div class="doc-card {theme}"><span class="doc-pill">{doc["type"]}</span>'
        f'<span class="doc-title">{clean_title(doc["title"])}</span><div class="doc-meta">{meta}</div></div>',
        unsafe_allow_html=True,
    )
    st.download_button("⬇️  Download PDF", pdf, file_name=doc["path"].split("/")[-1], mime="application/pdf",
                       type="primary", key=f"{key}_dl")
    st.pdf(pdf, height=950)


PO_INDEX_FILE = "production_index.json"  # Contour, Pinnacle & Signature lot POs (stored in Land_Contracts)
PO_BUILDERS_NOTE = "Contour, Pinnacle &amp; Signature Homes — pick the lot to see every PO, CO and contract"


def show_billing_pos():
    """Builder → Community → Lot → PO, for the PO builders (Contour, Pinnacle, Signature)."""
    if st.button("⬅  Back to Home", key="back_home_billing"):
        go_to_page("home")
    st.markdown(
        f"""
        <div class="contracts-hero theme-billing">
            <div class="section-kicker">Billing POs</div>
            <h1>Billing POs</h1>
            <p>{PO_BUILDERS_NOTE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    docs, error = load_document_index(LAND_REPO, PO_INDEX_FILE)
    if error:
        render_document_access_help(LAND_REPO, error)
        return
    if not docs:
        st.info("No lot POs loaded yet.")
        return

    cols = st.columns([1, 1.3, 1.3], gap="medium")
    builders = sorted({d["builder"] for d in docs})
    with cols[0]:
        builder = st.selectbox("1. Select Builder", builders, key="po_builder")
    pool = [d for d in docs if d["builder"] == builder]
    communities = sorted({d["community"] for d in pool}, key=lambda c: (c == "Master Contract", c.lower()))
    with cols[1]:
        community = st.selectbox("2. Select Community", communities, key=f"po_comm_{builder}")
    pool = [d for d in pool if d["community"] == community]
    sections = sorted({(tuple(d["section_order"]), d["section"]) for d in pool})
    section_names = [name for _, name in sections]
    counts = {name: sum(1 for d in pool if d["section"] == name) for name in section_names}
    with cols[2]:
        section = st.selectbox("3. Select Lot", section_names, key=f"po_lot_{builder}_{community}",
                               format_func=lambda n: f"{n}  ({counts[n]})")
    lot_docs = sorted([d for d in pool if d["section"] == section], key=lambda d: d.get("date", ""), reverse=True)

    def label(i):
        d = lot_docs[i]
        title = re.sub(r"^\d{4}-\d{2}-\d{2}\s*-\s*", "", d["title"])
        title = title.replace(f'{community} - ', "").replace("Production - ", "")
        date = f' · {pd.Timestamp(d["date"]).strftime("%m/%d/%Y")}' if d.get("date") else ""
        return f'{d["type"]} — {title}{date}'

    pick = st.selectbox("4. Select PO / Document", list(range(len(lot_docs))), format_func=label,
                        key=f"po_doc_{builder}_{community}_{section}")
    st.caption(f'{len(lot_docs)} document{"s" if len(lot_docs) != 1 else ""} for **{community} · {section}** '
               f'· {len(pool)} total for {community}')
    doc = lot_docs[pick]
    try:
        with st.spinner("Loading PDF…"):
            pdf = load_document_pdf(LAND_REPO, doc["path"])
    except Exception as exc:
        st.error(f"Could not open this PDF: {exc}")
        return
    date = pd.Timestamp(doc["date"]).strftime("%m/%d/%Y") if doc.get("date") else ""
    meta = " · ".join(x for x in [builder, community, section, date, f'{int(doc.get("size_kb", 0)):,} KB'] if x)
    title = re.sub(r"^\d{4}-\d{2}-\d{2}\s*-\s*", "", doc["title"])
    st.markdown(
        f'<div class="doc-card po"><span class="doc-pill">{doc["type"]}</span>'
        f'<span class="doc-title">{title}</span><div class="doc-meta">{meta}</div></div>',
        unsafe_allow_html=True,
    )
    st.download_button("⬇️  Download PDF", pdf, file_name=doc["path"].split("/")[-1], mime="application/pdf",
                       type="primary", key="po_dl")
    st.pdf(pdf, height=950)


def show_customs_documents():
    if st.button("⬅  Back to Home", key="back_home_customs"):
        go_to_page("home")

    st.markdown(
        """
        <div class="contracts-hero theme-customs">
            <div class="section-kicker">Customs</div>
            <h1>Customs Contracts</h1>
            <p>Signed proposals, contracts, change orders & payment schedules</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_document_browser(CUSTOMS_REPO, "customs_docs", "", two_level=False, job_label="Customer / Job")

    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("📁 Other Customs documents (plans, waivers, photos) on OneDrive", CUSTOMS_SHARED_URL,
                   use_container_width=True)


def show_land_documents():
    if st.button("⬅  Back to Home", key="back_home_land"):
        go_to_page("home")

    st.markdown(
        """
        <div class="contracts-hero theme-land">
            <div class="section-kicker">Commercial</div>
            <h1>Commercial Contracts</h1>
            <p>Streetscapes, model complexes &amp; common areas</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_document_browser(LAND_REPO, "land_docs", "land", two_level=True, group_label="Builder",
                            job_label="Community / Project")


DIVISION_TILES = [
    ("production", "Production", "Builder landscape & paver contracts", "production_builders"),
    ("concrete", "Concrete", "Foundations, flatwork & driveways", "concrete_builders"),
    ("pergolas", "Patios & Pergolas", "Patio cover & pergola pricing", "pergolas"),
    ("maintenance", "Maintenance", "Monthly revenue & contracts", "maintenance_home"),
    ("customs", "Customs", "Custom job contracts", "customs_documents"),
    ("land", "🏢 Commercial", "Streetscapes, models & common areas", "land_documents"),
    ("billing", "🧾 Billing POs", "Contour, Pinnacle & Signature lot POs", "billing_pos"),
]


@st.cache_data(ttl=300)
def community_index():
    """Every community in the app for the home-page search:
    (display_community, builder, division, archived, community, display_builder)."""
    rows = []
    for builder_name in BUILDER_ORDER:
        try:
            data = load_builder_data(builder_name)
        except Exception:
            continue
        if data is None or data.empty:
            continue
        mask = concrete_mask(data)
        for division in ("production", "concrete"):
            part = data[mask] if division == "concrete" else data[~mask]
            archived_set = ARCHIVED_COMMUNITIES.get((builder_name, division), set())
            for community in sort_display_values(part["Community"].dropna().unique()):
                name = str(community)
                if name.lower().endswith(" - concrete"):
                    name = name[: -len(" - concrete")]
                shown_builder = builder_name
                if builder_name == "Other Builders" and " - " in name:
                    shown_builder, name = name.split(" - ", 1)
                rows.append((name, builder_name, division, community in archived_set, community, shown_builder))
    try:
        pergolas = load_contract_workbook(PERGOLAS_FILE, "Pergolas")
        for community in sort_display_values(pergolas["Community"].dropna().unique()):
            prefix, _, name = str(community).partition(" - ")
            shown_builder = PERGOLA_BUILDER_NAMES.get(prefix, prefix) if name else ""
            rows.append((name or community, "Pergolas", "pergolas", False, community, shown_builder))
    except Exception:
        pass
    po_docs, _ = load_document_index(LAND_REPO, PO_INDEX_FILE)
    for builder, community in sorted({(d["builder"], d["community"]) for d in po_docs}):
        if community != "Master Contract":
            rows.append((community, builder, "po", False, community, builder))
    for repo, division in ((CUSTOMS_REPO, "customs"), (LAND_REPO, "land")):
        docs, error = load_document_index(repo)
        seen = set()
        for d in docs:
            if (d["group"], d["job"]) in seen:
                continue
            seen.add((d["group"], d["job"]))
            group = "" if d["group"] == "Custom Homes" else doc_group_label(d["group"])
            rows.append((d["job"], d["group"], division, False, d["job"], group or "Custom Home"))
    return rows


PERGOLA_BUILDER_NAMES = {"KB": "KB Homes", "Century": "Century Communities"}


SEARCH_ALIASES = {"lake las vegas": "llv", "mountain falls": "mfllc mtn falls"}


def _norm(text):
    text = str(text).lower()
    for ch in ".@_-/()&,":
        text = text.replace(ch, " ")
    return " ".join(text.split())


def search_communities(query, limit=15):
    tokens = _norm(query).split()
    if not tokens:
        return [], 0
    scored = []
    for row in community_index():
        shown_name, builder_name, division, archived, community, shown_builder = row
        name = _norm(shown_name)
        for long_name, short in SEARCH_ALIASES.items():
            if long_name in name:
                name += " " + short
        haystack = f"{name} {_norm(shown_builder)} {_norm(builder_name)} {division}"
        if not all(token in haystack for token in tokens):
            continue
        q = " ".join(tokens)
        if name.startswith(q):
            score = 0
        elif all(token in name for token in tokens):
            score = 1
        else:
            score = 2  # matched on builder / division name
        scored.append((score, archived, name, row))
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    return [item[3] for item in scored[:limit]], len(scored)


def jump_to_search_result(match):
    _, builder_name, division, archived, community, _ = match
    if division == "po":
        st.session_state["po_builder"] = builder_name
        st.session_state[f"po_comm_{builder_name}"] = community
        st.session_state["home_q"] = ""
        set_page("billing_pos")
        return
    if division in ("customs", "land"):
        if division == "customs":
            job = community if builder_name == "Custom Homes" else f"{builder_name} › {community}"
            st.session_state["customs_docs_job"] = job
            page = "customs_documents"
        else:
            st.session_state["land_docs_group"] = builder_name
            st.session_state["land_docs_job"] = community
            page = "land_documents"
        st.session_state["home_q"] = ""
        set_page(page)
        return
    if division == "pergolas":
        prefix, page = "pergolas", "pergolas"
    else:
        slug = BUILDER_SLUGS[builder_name]
        prefix = f"{slug}_{division}_{'archived' if archived else 'active'}"
        page = f"{division}_{slug}" + ("_archived" if archived else "")
    st.session_state[f"{prefix}_community"] = community
    st.session_state.pop(f"{prefix}_series", None)
    st.session_state.pop(f"{prefix}_scar_date", None)
    st.session_state["home_q"] = ""
    set_page(page)


def show_contracts_home():
    inject_tile_logo_css()
    st.markdown(
        """
        <div class="contracts-hero hero-center">
            <div class="section-kicker">Alpha Landscapes · Contract Database</div>
            <h1>Contracts</h1>
            <p>Search any community, or pick a division below.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="home_search_box"):
        query = st.text_input(
            "🔎 Find a community",
            placeholder="Type a community or customer (e.g. Aries, LLV, Esplanade, Kim, Bruner) and press Enter",
            key="home_q",
        )
        if query.strip():
            hits, total = search_communities(query)
            if not hits:
                st.caption(f'No communities match "{query.strip()}".')
            else:
                st.caption(
                    f"{total} match{'es' if total != 1 else ''}"
                    + (f" — showing the first {len(hits)}" if total > len(hits) else "")
                    + " · click one to open it"
                )
                for i, row in enumerate(hits):
                    shown_name, builder_name, division, archived, community, shown_builder = row
                    division_name = {"pergolas": "Patios & Pergolas", "land": "Commercial", "po": "Billing POs"}.get(division, division.title())
                    label = f"**{shown_name}**  —  {shown_builder}  —  {division_name}" + ("  (archived)" if archived else "")
                    st.button(
                        label,
                        key=f"hit_{division}_{i}",
                        on_click=jump_to_search_result,
                        args=(row,),
                        use_container_width=True,
                    )

    def tile(column, item):
        key, label, note, page = item
        with column:
            if st.button(label, key=f"tile_{key}", use_container_width=True):
                go_to_page(page)
            st.markdown(f'<div class="tile-note">{note}</div>', unsafe_allow_html=True)

    row1 = st.columns(3, gap="large")
    for column, item in zip(row1, DIVISION_TILES[:3]):
        tile(column, item)
    row2 = st.columns(3, gap="large")
    for column, item in zip(row2, DIVISION_TILES[3:6]):
        tile(column, item)
    row3 = st.columns(3, gap="large")
    for column, item in zip(row3[1:], DIVISION_TILES[6:]):
        tile(column, item)


def show_pergolas():
    left, right = st.columns([4, 1])
    with left:
        if st.button("⬅  Back to Home", key="back_home_pergolas"):
            go_to_page("home")
    with right:
        if st.button("Refresh Data", key="refresh_pergolas", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown(
        """
        <div class="contracts-hero theme-pergolas">
            <div class="section-kicker">All Builders</div>
            <h1>Patios &amp; Pergolas</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data = load_contract_workbook(PERGOLAS_FILE, "Pergolas")
    render_contract_browser(data, "pergolas", "Pergolas")


def builder_button(builder_name, division, button_type="secondary"):
    slug = BUILDER_SLUGS[builder_name]
    if st.button(
        builder_name,
        key=f"builder_{division}_{slug}",
        type=button_type,
        use_container_width=True,
    ):
        go_to_page(f"{division}_{slug}")


def show_builder_home(division):
    label = "Concrete" if division == "concrete" else "Production"
    inject_builder_logo_css(division)
    if st.button("⬅  Back to Home", key=f"back_home_{division}"):
        go_to_page("home")

    st.markdown(
        f"""
        <div class="contracts-hero theme-{division}">
            <div class="section-kicker">{label}</div>
            <h1>{label} Contracts</h1>
            <p>Pick a builder</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    counts = {}
    for _, builder_name, div, archived, *_ in community_index():
        if div == division and not archived:
            counts[builder_name] = counts.get(builder_name, 0) + 1

    def cell(column, builder_name):
        with column:
            builder_button(builder_name, division)
            n = counts.get(builder_name, 0)
            text = f'{n} active communit{"y" if n == 1 else "ies"}' if n else "No contracts loaded yet"
            st.markdown(
                f'<div class="builder-count">{text}</div>',
                unsafe_allow_html=True,
            )

    with st.container(key=f"grid_{division}"):
        names = BUILDER_ORDER
        for start in range(0, len(names) - 2, 3):
            row = st.columns(3, gap="large")
            for column, builder_name in zip(row, names[start:start + 3]):
                cell(column, builder_name)
        last = st.columns([0.5, 1, 1, 0.5], gap="large")
        for column, builder_name in zip(last[1:3], names[6:]):
            cell(column, builder_name)


def show_builder_contracts(builder_name, division):
    label = "Concrete" if division == "concrete" else "Production"
    slug = BUILDER_SLUGS[builder_name]

    left, mid, right = st.columns([1.6, 2.4, 1])
    with left:
        if st.button(f"⬅  Back to {label}", key=f"back_{division}_{slug}", use_container_width=True):
            go_to_page(f"{division}_builders")
    with mid:
        if st.button("🏠  Home", key=f"homebtn_{division}_{slug}"):
            go_to_page("home")
    with right:
        if st.button("Refresh Data", key=f"refresh_{division}_{slug}", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown(
        f"""
        <div class="contracts-hero theme-{division}">
            <div class="section-kicker">Contracts › {label} › {builder_name}</div>
            <h1>{builder_name} {label} Contracts</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_data = load_builder_data(builder_name)

    if builder_name == "Pulte" and division == "concrete":
        loaded = set(all_data["Community"].dropna().unique())
        missing = EXPECTED_PULTE_CONCRETE - loaded
        if missing:
            st.warning("Missing concrete communities: " + ", ".join(sorted(missing)))

    active_data = get_division_data(all_data, builder_name, division, archived=False)
    render_contract_browser(active_data, f"{slug}_{division}_active", builder_name)

    if builder_name == "Other Builders" and division == "production":
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧾  Contour / Pinnacle / Signature lot POs → Billing POs", key="goto_billing_pos",
                     use_container_width=True):
            go_to_page("billing_pos")

    archive_set = ARCHIVED_COMMUNITIES.get((builder_name, division), set())
    if archive_set:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(
            '<div class="archive-note">Completed communities</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns([4, 1.5, 4])
        with cols[1]:
            if st.button("Archived Jobs", key=f"archive_{division}_{slug}", use_container_width=True):
                go_to_page(f"{division}_{slug}_archived")


def show_builder_archived(builder_name, division):
    label = "Concrete" if division == "concrete" else "Production"
    slug = BUILDER_SLUGS[builder_name]

    left, right = st.columns([2.2, 3.8])
    with left:
        if st.button(f"⬅  Back to {builder_name} {label}", key=f"back_archive_{division}_{slug}", use_container_width=True):
            go_to_page(f"{division}_{slug}")
    with right:
        if st.button("🏠  Home", key=f"homebtn_archive_{division}_{slug}"):
            go_to_page("home")

    st.markdown(
        f"""
        <div class="contracts-hero theme-archived">
            <div class="section-kicker">Contracts › {label} › {builder_name}</div>
            <h1>Archived Jobs</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data = load_builder_data(builder_name)
    archived = get_division_data(data, builder_name, division, archived=True)
    render_contract_browser(archived, f"{slug}_{division}_archived", builder_name)


def show_builder_placeholder(division, builder_name):
    label = "Concrete" if division == "concrete" else "Production"
    slug = BUILDER_SLUGS[builder_name]
    if st.button(f"⬅  Back to {label}", key=f"back_placeholder_{division}_{slug}"):
        go_to_page(f"{division}_builders")

    st.markdown(
        f"""
        <div class="contracts-hero theme-{division}">
            <div class="section-kicker">{label}</div>
            <h1>{builder_name} Contracts</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("No contracts loaded.")


# The web address is the source of truth for which page is showing, so the
# browser back arrow works. No ?page= in the address means the home page.
page = st.query_params.get("page") or "home"
st.session_state["contracts_page"] = page

if page == "home":
    show_contracts_home()
elif page == "production_builders":
    show_builder_home("production")
elif page == "concrete_builders":
    show_builder_home("concrete")
elif page == "maintenance_home":
    show_maintenance_home()
elif page == "maintenance_revenue":
    show_maintenance_revenue()
elif page == "customs_documents":
    show_customs_documents()
elif page == "billing_pos":
    show_billing_pos()
elif page == "land_documents":
    show_land_documents()
elif page == "pergolas":
    show_pergolas()
else:
    handled = False
    for division in ("production", "concrete"):
        prefix = f"{division}_"
        if not page.startswith(prefix):
            continue

        route = page[len(prefix):]
        archived = route.endswith("_archived")
        slug = route[:-9] if archived else route

        builder_name = next((name for name, value in BUILDER_SLUGS.items() if value == slug), None)
        if builder_name:
            if builder_name in ACTIVE_BUILDERS:
                if archived:
                    show_builder_archived(builder_name, division)
                else:
                    show_builder_contracts(builder_name, division)
            else:
                show_builder_placeholder(division, builder_name)
            handled = True
            break

    if not handled:
        go_to_page("home")

st.markdown("---")
st.markdown(
    '<div class="app-footer">Created and maintained by Alejandro Escutia | © 2024-2026</div>',
    unsafe_allow_html=True,
)
