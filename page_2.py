import streamlit as st
import datetime
import pytz
import requests
from streamlit.components.v1 import html

from streamlit_radar_component import rainviewer_radar
from streamlit_extras.floating_button import floating_button

from streamlit_scroll_to_top import scroll_to_here

def spacing(px=20):
    st.markdown(f"<div style='margin-top: {px}px;'></div>", unsafe_allow_html=True)

if 'scroll_to_top' not in st.session_state:
    st.session_state.scroll_to_top = False

if st.session_state.scroll_to_top:
    scroll_to_here(1, key='top')  # Scroll to the top of the page, 0 means instantly, but you can add a delay (im milliseconds)
    st.session_state.scroll_to_top = False  # Reset the state after scrolling

def scroll():
    st.session_state.scroll_to_top = True

#region Gestione timestamp
@st.cache_data(ttl=300)  # Cache per 5 minuti per non sovraccaricare l'API
def get_rainviewer_timestamps():
    try:
        response = requests.get("https://api.rainviewer.com/public/weather-maps.json")
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP
        data = response.json()
        datasatellite = data.get("satellite", {}).get("infrared", [])
        satellite_data = {
            i["time"]: i["path"] for i in datasatellite
        }
        dataparsed = data.get('radar', {}).get('past', [])
        datareturn = {"radar": [i["time"] for i in dataparsed],
                      "satellite": satellite_data
        }
        return datareturn
    except requests.exceptions.RequestException as e:
        st.error(f"Errore nel recupero dei timestamp da Rainviewer: {e}")
        return []

def update_timestamps():
    st.session_state['timestamps_utc'] = get_rainviewer_timestamps()

def format_timestamp(timestamp_utc):
    local = datetime.datetime.fromtimestamp(timestamp_utc, tz=pytz.timezone(st.session_state["user_timezone"] if st.session_state["user_timezone"] else 'UTC'))
    return local.strftime("%Y-%m-%d %H:%M:%S")

top = floating_button(":material/arrow_upward:", on_click=scroll)



st.markdown("## RADAR METEO\n"
            "---")

colorschemes = [
    ("Black and White", 0),
    ("Original", 1),
    ("Universal Blue", 2),
    ("TITAN", 3),
    ("The Weather Channel", 4),
    ("Meteored", 5),
    ("NEXRAD Level III", 6),
    ("Rainbow @ SELEX-IS", 7),
    ("Dark Sky", 8)
]


st.sidebar.markdown("## Impostazioni Radar")

with st.sidebar:
    with st.container(border=True):
        st.session_state.mode = st.selectbox("Modalità radar",
                                             options=["Radar", "Satellite"])
        spacing()
        st.session_state.smoothing = st.checkbox("Smoothing dati", value=True)
        spacing()
        st.session_state.colorscheme = st.selectbox("Schema colori", options=colorschemes, format_func=lambda x:x[0], index = 7)[1]
        spacing()
        st.button("Aggiorna dati", icon=":material/radar:", on_click=update_timestamps)
st.sidebar.markdown("---")









update_timestamps()






if 'timestamps_utc' not in st.session_state:
    update_timestamps()


if st.session_state.mode == "Radar":
    formatted_times = [format_timestamp(ts) for ts in st.session_state.timestamps_utc["radar"]]
    timestamp_mapping = dict(zip(formatted_times, st.session_state.timestamps_utc["radar"]))
else:
    formatted_times = [format_timestamp(ts) for ts in st.session_state.timestamps_utc["satellite"]]
    timestamp_mapping = dict(zip(formatted_times, st.session_state.timestamps_utc["satellite"]))
#endregion

select_timestamp = st.select_slider(
    "Seleziona data e ora",
    options=formatted_times,
    value=formatted_times[len(formatted_times) - 1],
)

selected_timestamp_utc = timestamp_mapping[select_timestamp] if (st.session_state.mode == "Radar") else (
    st.session_state.timestamps_utc["satellite"][timestamp_mapping[select_timestamp]]
)




if selected_timestamp_utc:
    rainviewer_radar(
        selected_timestamp_utc,
        colorscheme=st.session_state.colorscheme,
        smoothing=int(st.session_state.smoothing),
        key="radarview",
        height=400,
        satellite=st.session_state.mode=="Satellite",
        apikey=st.secrets["map_key"]
    )

st.markdown("""---
Mappa Fulmini
""")
spacing()
st.markdown('<iframe src="https://map.blitzortung.org/index.php?interactive=1&NavigationControl=1&FullScreenControl=1&Cookies=0&InfoDiv=1&MenuButtonDiv=1&ScaleControl=1&LinksCheckboxChecked=0&LinksRangeValue=10&MapStyle=0&MapStyleRangeValue=4&LightningRangeValue=2&Advertisment=0#6/46/10" width="100%" height="800"></iframe>', unsafe_allow_html=True )
