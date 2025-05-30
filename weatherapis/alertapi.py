import json

import requests
from urllib.parse import urlencode
import re

import streamlit as st


def separa_testi_per_lingua(alertdesc):
    pattern = r'([A-Za-z]+)\(([\w-]+)\):\s*(.*?)(?=(?:[A-Za-z]+\([\w-]+\):)|$)'
    risultati = re.findall(pattern, alertdesc, re.DOTALL)

    # Normalizzazione codice lingua (es. "en-GB" -> "en")
    def normalizza_codice(codice):
        return codice.split('-')[0].lower()

    return {
        normalizza_codice(codice): testo.strip()
        for _, codice, testo in risultati
    }

def match_advisory(lang, advisory):
    matcher = {
        "it": {
            "Advisory": "Giallo 🟨",
            "Watch": "Arancione 🟧",
            "Warning": "Rosso 🟥"
        },
        "en": {
            "Advisory": "Yellow 🟨",
            "Watch": "Orange 🟧",
            "Warning": "Red 🟥"
        },

    }
    if lang in matcher.keys():
        return matcher[lang][advisory]
    else:
        lang = "en"
        return matcher[lang][advisory]



class AlertAPI:
    def __init__(self):
        self.url = "https://api.weatherbit.io/v2.0/"
        self.key = st.secrets["alert_key"]

    def get_alerts(self, lat, lon):
        urlformat = self.url + "alerts/?" + urlencode({"lat": lat, "lon": lon, "key": self.key})
        response = requests.get(urlformat)
        jsonresponse = response.json()

        alerts = jsonresponse["alerts"]
        for alert in alerts:
            alert["description"] = separa_testi_per_lingua(alert["description"])
            alert["severity"] = {lang: match_advisory(lang, alert["severity"]) for lang in list(alert["description"].keys())}
        jsonresponse["alerts"] = alerts


        return jsonresponse


if __name__ == "__main__":
    api = AlertAPI()
    with open("test.json", "w", encoding="utf-8") as f:
        cuneo = (44.23, 7.33)
        banjaluka = (44.46, 17.11)
        test = (43.59,  20.53)
        f.write(json.dumps(api.get_alerts(*test), indent=4))