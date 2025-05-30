import requests
import streamlit as st
import plotly.express as px
from streamlit_searchbox import st_searchbox
import weatherapis.weatherapi as weatherapi
import weatherapis.chartsapi as chartsapi
from streamlit_extras.grid import grid
from urllib.parse import urlencode
from datetime import datetime
from zoneinfo import ZoneInfo
from babel.dates import format_datetime
import aiohttp
import asyncio
import time
import weatherapis.alertapi as alertapi
from components.alertst import st_weather_alert

# Funzione asincrona per scaricare l'immagine
async def fetch_image(url):
    print(f"Avvio fetch asincrono per: {url}")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Solleva un'eccezione per status HTTP >= 400
                print(f"Immagine scaricata ({response.status}) da: {url}")
                return await response.read()  # restituisce i bytes dell'immagine
        except aiohttp.ClientError as e:
            st.error(f"Errore durante il download dell'immagine: {e}")
            print(f"Errore aiohttp: {e}")
            return None # Restituisce None in caso di errore


@st.dialog("Prodotti Chart", width="large")
def modal_list_products():
    maxlen = 65
    listofproducts = st.session_state.chartapi.get_available_products()
    gridlayout = grid(3)
    for product in listofproducts:
        with gridlayout.container(border=True, height=220):
            st.markdown("#### "+(product["title"] if len(product["title"])<maxlen else product["title"][:maxlen-1]+"..." ))
            st.image(product["thumbnail"])

@st.dialog("Informazioni")
def modal_product_description(product):
    st.markdown("""
            <script>
            window.scrollTo(0, -1000);
            </script>
        """, unsafe_allow_html=True)

    st.markdown(f"""
# {product["title"]}
{st.session_state.chartapi.get_wide_description(product["name"])}
""")
    st.image(product["thumbnail"])



def get_chart(product, querystringvalues):
    apiurl = f"https://charts.ecmwf.int/opencharts-api/v1/products/{product}/?{urlencode(querystringvalues)}"
    data = requests.get(apiurl).json()
    st.session_state.charturl = data["data"]["link"]["href"]








if not "measure" in st.session_state:
    st.session_state.measure =  {
    'date': '',  # La data non ha un'unità di misura standard
    'temperature_2m': '°C',
    'weather_code': 'wmo',  # Il codice meteo non ha un'unità di misura numerica
    'precipitation_probability': '%',
    'apparent_temperature': '°C',
    'dew_point_2m': '°C',
    'relative_humidity_2m': '%',
    'surface_pressure': 'hPa',
    'temperature_1000hPa': '°C',
    'temperature_925hPa': '°C',
    'temperature_800hPa': '°C',
    'temperature_100hPa': '°C',
    'temperature_250hPa': '°C',
    'temperature_500hPa': '°C',
    'temperature_200hPa': '°C',
    'temperature_400hPa': '°C',
    'temperature_700hPa': '°C',
    'temperature_900hPa': '°C',
    'temperature_975hPa': '°C',
    'temperature_150hPa': '°C',
    'temperature_300hPa': '°C',
    'temperature_600hPa': '°C',
    'temperature_850hPa': '°C',
    'temperature_950hPa': '°C',
    'relative_humidity_1000hPa': '%',
    'relative_humidity_800hPa': '%',
    'relative_humidity_925hPa': '%',
    'relative_humidity_500hPa': '%',
    'relative_humidity_250hPa': '%',
    'relative_humidity_100hPa': '%',
    'relative_humidity_200hPa': '%',
    'relative_humidity_400hPa': '%',
    'relative_humidity_700hPa': '%',
    'relative_humidity_900hPa': '%',
    'relative_humidity_975hPa': '%',
    'relative_humidity_150hPa': '%',
    'relative_humidity_300hPa': '%',
    'relative_humidity_600hPa': '%',
    'relative_humidity_850hPa': '%',
    'relative_humidity_950hPa': '%',
    'wind_speed_100hPa': 'km/h',
    'wind_speed_250hPa': 'km/h',
    'wind_speed_500hPa': 'km/h',
    'wind_speed_800hPa': 'km/h',
    'wind_speed_1000hPa': 'km/h',
    'wind_speed_925hPa': 'km/h',
    'wind_speed_200hPa': 'km/h',
    'wind_speed_400hPa': 'km/h',
    'wind_speed_700hPa': 'km/h',
    'wind_speed_900hPa': 'km/h',
    'wind_speed_975hPa': 'km/h',
    'wind_speed_150hPa': 'km/h',
    'wind_speed_300hPa': 'km/h',
    'wind_speed_600hPa': 'km/h',
    'wind_speed_850hPa': 'km/h',
    'wind_speed_950hPa': 'km/h',
    'wind_direction_1000hPa': '°',
    'wind_direction_925hPa': '°',
    'wind_direction_500hPa': '°',
    'wind_direction_250hPa': '°',
    'wind_direction_100hPa': '°',
    'wind_direction_800hPa': '°',
    'wind_direction_400hPa': '°',
    'wind_direction_200hPa': '°',
    'wind_direction_900hPa': '°',
    'wind_direction_700hPa': '°',
    'wind_direction_975hPa': '°',
    'wind_direction_600hPa': '°',
    'wind_direction_150hPa': '°',
    'wind_direction_300hPa': '°',
    'wind_direction_850hPa': '°',
    'wind_direction_950hPa': '°',
    'geopotential_height_100hPa': 'm',
    'geopotential_height_250hPa': 'm',
    'geopotential_height_500hPa': 'm',
    'geopotential_height_800hPa': 'm',
    'geopotential_height_925hPa': 'm',
    'geopotential_height_1000hPa': 'm',
    'geopotential_height_200hPa': 'm',
    'geopotential_height_400hPa': 'm',
    'geopotential_height_700hPa': 'm',
    'geopotential_height_900hPa': 'm',
    'geopotential_height_975hPa': 'm',
    'geopotential_height_150hPa': 'm',
    'geopotential_height_300hPa': 'm',
    'geopotential_height_600hPa': 'm',
    'geopotential_height_950hPa': 'm',
    'geopotential_height_850hPa': 'm',
    'cloud_cover': '%',
    'wind_speed_10m': 'km/h',
    'wind_gusts_10m': 'km/h',
    'wind_direction_10m': '°',
    'cape': 'J/Kg',
    'lifted_index': 'K',
    'convective_inhibition': 'J/Kg',
    'uv_index': 'unità',
    'srh_pos': 'm²/s²',
    'srh_neg': 'm²/s²',
    'srh_tot': 'm²/s²',
    'bunkers_right': 'km/h',
        'bunkers_left': 'km/h',
        'bunkers_mean': 'km/h',
        'condizione_meteo_ita' : '',
        'cape_mean': 'J/kg',
        'sunset': '',
        'sunrise': '',
        'cape_max': 'J/kg',
        "temperature_2m_min": '°C',
        "temperature_2m_max": '°C',
        "apparent_temperature_mean": '°C',
        'precipitation_probability_max': '%',
        'uv_index_max': '',
        'lightning_potential': '',
        "bulk_shear": "kts"

}

def download_alerts():
    if st.session_state.city is None:
        return
    st.session_state.alerts = st.session_state.alertapi.get_alerts(st.session_state.city[1], st.session_state.city[0])

#region Downloads
def download_weather(citypassed = None):
    if citypassed is None:
        city = st.session_state.city
    else:
        city = citypassed
    tempdata = st.session_state.weatherapi.requestweather(city[0], city[1], city[2])
    st.session_state.hourly = tempdata[1]
    #hourly.set_index('date', inplace=True)
    #hourly["date"] = pd.to_datetime(hourly["date"])

    st.session_state.daily = tempdata[0]
    st.session_state.minutely = tempdata[2]

    if "weather_code" in st.session_state.hourly.columns:
        st.session_state.hourly['condizione_meteo_ita'] = st.session_state.hourly['weather_code'].apply(
            weatherapi.get_condizione_meteo_italiano)
    if 'weather_code' in st.session_state.daily.columns:
        st.session_state.daily['condizione_meteo_ita'] = st.session_state.daily['weather_code'].apply(
            weatherapi.get_condizione_meteo_italiano)
    if 'weather_code' in st.session_state.minutely.columns:
        st.session_state.minutely['condizione_meteo_ita'] = st.session_state.minutely['weather_code'].apply(
            weatherapi.get_condizione_meteo_italiano)


#endregion

st.title("Dati Meteo")
st.markdown("#####")


if not 'hourly' in st.session_state:
    st.session_state.hourly = None

if not 'daily' in st.session_state:
    st.session_state.daily = None

if not 'minutely' in st.session_state:
    st.session_state.minutely = None

if not 'city' in st.session_state:
    st.session_state.city = None




if not 'weatherapis' in st.session_state:
    st.session_state.weatherapi = weatherapi.ApiWeather()

if not 'chartapi' in st.session_state:
    st.session_state.chartapi = chartsapi.ChartsAPI()

if not 'charturl' in st.session_state:
    st.session_state.charturl = None

if not 'imagecaption' in st.session_state:
    st.session_state.imagecaption = None

if not 'alertapi' in st.session_state:
    st.session_state.alertapi = alertapi.AlertAPI()


st.markdown("---")
st.session_state.city = st_searchbox(st.session_state.weatherapi.requestgeocode, "Cerca città", key="searchbox", debounce=800 , submit_function=download_weather)
st.markdown("")
btt1, btt2 = st.columns(2)
with st.container(border=True):
    with btt1:
        st.button("Ricarica dati meteo", "reloadweather", None, download_weather, disabled=not st.session_state.city)
    with btt2:
        st.button("Ricarica allerte meteo", "reloadalerts", None, download_alerts, disabled=not st.session_state.city)

st.markdown(f"---\n{'' if st.session_state.city else 'Seleziona una città per avere grafici e allerte'}")



if st.session_state.hourly is not None and st.session_state.daily is not None and st.session_state.minutely is not None:
    extend = st.expander("Dati Grafici")
    with extend:
        tab1, tab2, tab3 = st.tabs(["Dati orari", "Dati giornalieri", "Dati ogni 15 minuti"])
        with tab1:
            listavars : list =  st.session_state.hourly.columns.tolist()
            listavars.remove("date")
            listaelab = [item.replace("_", " ").title() for item in listavars]
            st.session_state.selectboxhourly = st.selectbox("Variabile oraria", key="selectbox", options=listaelab)
            fig = px.line(st.session_state.hourly, x="date", y=st.session_state.selectboxhourly.replace(" ", "_").lower().replace("hpa", "hPa"),
                          labels={st.session_state.selectboxhourly.replace(" ", "_").lower().replace("hpa", "hPa"): f'{st.session_state.selectboxhourly} ({st.session_state.measure[st.session_state.selectboxhourly.replace(" ", "_").lower().replace("hpa", "hPa")]})', 'date': 'Orario'},
                          title='Grafico Orario', line_shape='spline')
            if st.session_state.selectboxhourly == "Weather Code" and 'condizione_meteo_ita' in st.session_state.hourly.columns:
                hovertemplate_str = '<b>Data e Ora</b>: %{x|%Y-%m-%d %H:%M:%S}<br><b>Codice Meteo</b>: %{y}<br><b>Condizione</b>: %{customdata[0]}<extra></extra>'
                customdata_list = st.session_state.hourly[['condizione_meteo_ita']].values.tolist()
                fig.update_traces(hovertemplate=hovertemplate_str, customdata=customdata_list)
            else:
                fig.update_traces(hovertemplate=f'<b>Data e Ora</b>: %{{x|%Y-%m-%d %H:%M:%S}}<br><b>{st.session_state.selectboxhourly}</b>: %{{y}} {st.session_state.measure[st.session_state.selectboxhourly.replace(" ", "_").lower().replace("hpa", "hPa")]}<extra></extra>')
            st.plotly_chart(fig)
        with tab2:
            listavars: list = st.session_state.daily.columns.tolist()
            listavars.remove("date")
            listaelab = [item.replace("_", " ").title() for item in listavars]
            st.session_state.selectboxdaily = st.selectbox("Variabile giornaliera", options=listaelab)
            fig = px.line(st.session_state.daily, x="date",
                          y=st.session_state.selectboxdaily.replace(" ", "_").lower().replace("hpa", "hPa"),
                          labels={st.session_state.selectboxdaily.replace(" ", "_").lower().replace("hpa",
                                                                                                     "hPa"): f'{st.session_state.selectboxdaily} ({st.session_state.measure[st.session_state.selectboxdaily.replace(" ", "_").lower().replace("hpa", "hPa")]})',
                                  'date': 'Data'},
                          title='Grafico Giornaliero', line_shape='spline')
            if st.session_state.selectboxdaily == "Weather Code" and 'condizione_meteo_ita' in st.session_state.daily.columns:
                hovertemplate_str = '<b>Data e Ora</b>: %{x|%Y-%m-%d %H:%M:%S}<br><b>Codice Meteo</b>: %{y}<br><b>Condizione</b>: %{customdata[0]}<extra></extra>'
                customdata_list = st.session_state.daily[['condizione_meteo_ita']].values.tolist()
                fig.update_traces(hovertemplate=hovertemplate_str, customdata=customdata_list)
            else:
                fig.update_traces(
                    hovertemplate=f'<b>Data e Ora</b>: %{{x|%Y-%m-%d %H:%M:%S}}<br><b>{st.session_state.selectboxdaily}</b>: %{{y}} {st.session_state.measure[st.session_state.selectboxdaily.replace(" ", "_").lower().replace("hpa", "hPa")]}<extra></extra>')
            st.plotly_chart(fig)
        with tab3:
            listavars: list = st.session_state.minutely.columns.tolist()
            listavars.remove("date")
            listaelab = [item.replace("_", " ").title() for item in listavars]
            st.session_state.selectboxminutely = st.selectbox("Variabile ogni 15 minuti", options=listaelab)
            fig = px.line(st.session_state.minutely, x="date",
                          y=st.session_state.selectboxminutely.replace(" ", "_").lower().replace("hpa", "hPa"),
                          labels={st.session_state.selectboxminutely.replace(" ", "_").lower().replace("hpa",
                                                                                                    "hPa"): f'{st.session_state.selectboxminutely} ({st.session_state.measure[st.session_state.selectboxminutely.replace(" ", "_").lower().replace("hpa", "hPa")]})',
                                  'date': 'Data'},
                          title='Grafico Giornaliero', line_shape='spline')
            if st.session_state.selectboxminutely == "Weather Code" and 'condizione_meteo_ita' in st.session_state.minutely.columns:
                hovertemplate_str = '<b>Data e Ora</b>: %{x|%Y-%m-%d %H:%M:%S}<br><b>Codice Meteo</b>: %{y}<br><b>Condizione</b>: %{customdata[0]}<extra></extra>'
                customdata_list = st.session_state.minutely[['condizione_meteo_ita']].values.tolist()
                fig.update_traces(hovertemplate=hovertemplate_str, customdata=customdata_list)
            else:
                fig.update_traces(
                    hovertemplate=f'<b>Data e Ora</b>: %{{x|%Y-%m-%d %H:%M:%S}}<br><b>{st.session_state.selectboxminutely}</b>: %{{y}} {st.session_state.measure[st.session_state.selectboxminutely.replace(" ", "_").lower().replace("hpa", "hPa")]}<extra></extra>')
            st.plotly_chart(fig)

if st.session_state.city is not None:
    alertextend = st.expander("Allerte Meteo")
    with alertextend:

        st.session_state.alerts = st.session_state.alertapi.get_alerts(st.session_state.city[1], st.session_state.city[0])
        st.session_state.weatheralertlanguage = st.selectbox("Lingua allerte", st.session_state.alerts["alerts"][0]["description"].keys())
        #st.markdown(st.session_state.alerts)
        for alert in st.session_state.alerts["alerts"]:
            st_weather_alert(alert)

extendcharts = st.expander("Chart meteo")

if "selectedProduct" not in st.session_state:
    st.session_state.selectedProduct = None

with extendcharts:
    st.button("Mostra tutti i prodotti", on_click=modal_list_products)
    st.session_state.selectedProduct = st_searchbox(st.session_state.chartapi.search_product, "Prodotto chart", "Ricerca prodotti chart", key="chartapisearchbox", debounce=20)
    if st.session_state.selectedProduct:
        axislist = st.session_state.chartapi.get_axis_list(st.session_state.selectedProduct["name"])
        axisnames = [axis[0] for axis in axislist]
        titleconversion = {axis[0]: axis[1] for axis in axislist}
        remainingaxis = axisnames.copy()
        values = {}
        if "area" in axisnames or "projection" in axisnames:
            availableareas = st.session_state.chartapi.get_available_area(st.session_state.selectedProduct["name"])
            selectedarea = st.selectbox("Area proiezione", [(area["label"], area["value"]) for area in availableareas],
                                        format_func=lambda x: x[0])
            #st.markdown(selectedarea)
            if "area" in axisnames:
                remainingaxis.remove("area")
                values["area"] = selectedarea[1]
            elif "projection" in axisnames:
                remainingaxis.remove("projection")
                values["projection"] = selectedarea[1]
            else:print("ERRORE ")

        if "base_time" in axisnames:
            availablebasetimes = st.session_state.chartapi.get_available_base_times(st.session_state.selectedProduct["name"])
            selectedbasetime = st.selectbox("Tempo run modello", ["latest"]+availablebasetimes, format_func=lambda x: x[0] if(type(x) == tuple) else x )
            if selectedbasetime == "latest":
                selectedbasetime = availablebasetimes[0]
            #st.markdown(selectedbasetime)
            remainingaxis.remove("base_time")
            values["base_time"] = selectedbasetime[0]
            if selectedbasetime:
                availablevalidtimes = st.session_state.chartapi.get_available_valid_times(st.session_state.selectedProduct["name"], selectedbasetime[1])
                if availablevalidtimes:
                    selectedavailabletime = st.select_slider("Step modello", options=availablevalidtimes, format_func=lambda x: x[0] )
                    #st.markdown(selectedavailabletime)
                    values["valid_time"] = selectedavailabletime[1]
                    dt = datetime.strptime(values["valid_time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))
                    parseddt = dt.astimezone(ZoneInfo(st.session_state.user_timezone))
                    st.markdown(f"""Data nella tua timezone:
{format_datetime(parseddt, "EEEE d MMMM y 'alle' HH:mm", locale='it')}""")
        for axis in remainingaxis:
            if axis == "location":
                st.session_state.citygram = st_searchbox(st.session_state.weatherapi.requestgeocode, "Cerca città",
                                                     key="searchbox-location-charts", debounce=800)
                if not st.session_state.citygram:
                    st.markdown("Inserisci la posizione nella casella sopra")
                else:
                    values["lat"] = st.session_state.citygram[1]
                    values["lon"] = st.session_state.citygram[0]
            else:
                selectedaxis = st.session_state.chartapi.get_available_values_random_axis(st.session_state.selectedProduct["name"], axis)
                values[axis] = st.selectbox(selectedaxis["title"], selectedaxis["values"], format_func=lambda x: x["label"])["value"]
                #st.markdown(values[axis])

        canrequest = False
        keys = list(values.keys())
        if "valid_time" in keys:
            keys.remove("valid_time")

        axischeck = axisnames.copy()
        if "location" in axischeck:
            axischeck.remove("location")
            axischeck.append("lat")
            axischeck.append("lon")
        if set(keys) == set(axischeck):
            canrequest = True
            st.session_state.imgcaption = f"{st.session_state.selectedProduct["title"]}"
        clm1, clm2 = st.columns(2)
        with clm1:
            st.button("Richiedi Chart", on_click=get_chart, disabled=not canrequest, args=(st.session_state.selectedProduct["name"], values))
        with clm2:
            st.button("Informazioni sul prodotto", on_click=modal_product_description, disabled=not canrequest,
                      args=(st.session_state.selectedProduct,), icon=":material/info:")
        if st.session_state.charturl:
            start = time.time()
            print("Visualizzando immagine")
            st.image(st.session_state.charturl, caption=st.session_state.selectedProduct["title"], use_container_width=True)
            print(f"Caricata immagine {(time.time() - start)}")
            cl1, cl2 = st.columns(2)
            with cl2:
                st.markdown(f"[🔍 Apri immagine a pieno schermo]({st.session_state.charturl})")
            with cl1:
                with st.spinner("Caricamento immagine per download"):
                    start_download = time.time()
                    imgbytes = None
                    try:
                        # Chiama asyncio.run direttamente sulla coroutine fetch_image
                        imgbytes = asyncio.run(fetch_image(st.session_state.charturl))
                    except RuntimeError as e:
                        # Potrebbe ancora capitare se Streamlit esegue in un thread con un loop già attivo
                        st.error(f"Errore Runtime asyncio: {e}. Prova ad usare la Soluzione 2 (requests).")
                        print(f"Errore runtime asyncio: {e}")
                    except Exception as e:
                        st.error(f"Errore imprevisto durante il download asincrono: {e}")
                        print(f"Errore imprevisto asyncio: {e}")

                    if imgbytes:
                        print(f"Tempo download bytes immagine: {(time.time() - start_download):.2f}s")
                        try:
                            # Estrai un nome file sensato dall'URL o dal titolo
                            filename_base = st.session_state.selectedProduct["name"]
                            if 'valid_time' in values:
                                try:
                                    dt_fn = datetime.strptime(values["valid_time"], "%Y-%m-%dT%H:%M:%SZ")
                                    filename_base += "_" + dt_fn.strftime("%Y%m%d_%H%M")
                                except ValueError:
                                    pass  # Ignora se il formato non è valido
                            filename = f"{filename_base}.png"  # ECMWF charts sono spesso PNG

                            st.download_button("Scarica immagine", imgbytes, file_name=filename, mime="image/png",
                                               key="download_image_btn")  # Specifica nome e mime
                        except Exception as e:
                            st.error(f"Errore durante la preparazione del download button: {e}")
                            print(f"Errore download button: {e}")
                    else:
                        st.warning("Download fallito o immagine non disponibile.")

        #st.markdown(values)


