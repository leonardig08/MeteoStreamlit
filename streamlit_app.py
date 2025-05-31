import streamlit as st
import pytz
import requests


hide_components_script = """
<script>
setTimeout(function() {
    // Nasconde il profilo autore
    const profile = document.querySelector('div[class^="_profileContainer_"]');
    if (profile) {
        profile.style.display = "none";
        console.log("Profilo nascosto");
    }

    // Nasconde il badge streamlit cloud
    const badge = document.querySelector('a[class^="_container_"][class*="_viewerBadge_"]');
    if (badge) {
        badge.style.display = "none";
        console.log("Badge nascosto");
    }

    // Intervallo per retry
    const interval = setInterval(() => {
        const profile = document.querySelector('div[class^="_profileContainer_"]');
        const badge = document.querySelector('a[class^="_container_"][class*="_viewerBadge_"]');
        if (profile) {
            profile.style.display = "none";
            console.log("Retry: profilo nascosto");
        }
        if (badge) {
            badge.style.display = "none";
            console.log("Retry: badge nascosto");
        }
        if (profile && badge) {
            clearInterval(interval);
        }
    }, 500);
}, 5000); // Delay iniziale di 3 secondi
</script>
"""

testscript = 'console.log("TEST")'




def is_connected():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

if not is_connected():
    st.markdown("# Connettiti ad internet")

else:
    st.set_page_config(layout="wide")



    with st.sidebar:
        st.session_state["user_timezone"] = st.selectbox("Seleziona fuso orario", pytz.common_timezones,
                                                         index=pytz.common_timezones.index("Europe/Rome"))
        st.markdown("---")


    homepage = st.Page("page_main.py", title="Dati meteo", icon=":material/thunderstorm:")
    page2 = st.Page("page_2.py", title="Radar e satellite", icon=":material/radar:")

    nav = st.navigation([homepage, page2])

    nav.run()
    st.markdown(testscript, unsafe_allow_html=True)
    st.markdown(hide_components_script, unsafe_allow_html=True)

