import streamlit as st
import pytz
import requests


hide_components_script = """
    <script>
    window.addEventListener('load', function() {
        // Nasconde il profilo autore
        const profile = document.querySelector('div[class^="_profileContainer_"]');
        if (profile) {
            profile.style.display = "none";
        }

        // Nasconde il badge streamlit cloud
        const badge = document.querySelector('a[class^="_container_"][class*="_viewerBadge_"]');
        if (badge) {
            badge.style.display = "none";
        }
    });

    // Ritenta se i componenti non sono caricati subito
    const interval = setInterval(() => {
        const profile = document.querySelector('div[class^="_profileContainer_"]');
        const badge = document.querySelector('a[class^="_container_"][class*="_viewerBadge_"]');
        if (profile) profile.style.display = 'none';
        if (badge) badge.style.display = 'none';
        if (profile && badge) clearInterval(interval);
    }, 500);
    </script>
"""





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

    st.markdown(hide_components_script, unsafe_allow_html=True)

