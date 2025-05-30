from zoneinfo import ZoneInfo

import streamlit as st
from datetime import datetime
from babel.dates import format_datetime


def format_date_time(date_str, lang='it', format_style='long'):
    LOCALE_MAP = {
        'it': 'it_IT',
        'en': 'en_US',
    }
    # Converti stringa ISO in oggetto datetime
    dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=ZoneInfo("UTC"))

    dt = dt.astimezone(ZoneInfo(st.session_state["user_timezone"]))

    # Ottieni locale completo dalla lingua
    locale = LOCALE_MAP.get(lang, 'en_US')  # default a inglese

    # Format della data secondo lingua e stile
    return format_datetime(dt, format=format_style, locale=locale)


def st_weather_alert(alert):

    with st.container(border= True):

        color = alert["severity"]["en"].split(" ")[0].lower()
        if color == "yellow":
            color = "orange"
        lang = st.session_state.weatheralertlanguage
        st.markdown(f"### :{color}[" + alert["title"] +" " + alert["severity"][
            lang if lang is not None else "en"] + "]")
        col1, col2 = st.columns(2)
        with col1:
            with st.popover("Dettagli" if lang=="it" else "Details"):
                st.markdown(alert["description"][lang])
        with col2:
            towrite = "Valido da " + format_date_time(alert["effective_utc"], lang) + ". Fino a " + format_date_time(alert["expires_utc"], lang) if lang=="it" else(
                "Valid from " + format_date_time(alert["effective_utc"], lang) + ". Expires " + format_date_time(alert["expires_utc"], lang)
            )
            st.markdown(towrite)

