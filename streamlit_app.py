import streamlit as st
import pytz
import requests


hide_components_script = """
    <script>
    window.addEventListener('load', function() {
        const profile = document.querySelector('div[class^="_profileContainer_"]');
        if (profile) {
            console.log("✅ Profilo autore trovato e nascosto (on load).");
            profile.style.display = "none";
        } else {
            console.log("⚠️ Profilo autore non trovato al primo tentativo.");
        }

        const badge = document.querySelector('a[class^="_container_"][class*="_viewerBadge_"]');
        if (badge) {
            console.log("✅ Badge Streamlit trovato e nascosto (on load).");
            badge.style.display = "none";
        } else {
            console.log("⚠️ Badge Streamlit non trovato al primo tentativo.");
        }
    });

    const interval = setInterval(() => {
        const profile = document.querySelector('div[class^="_profileContainer_"]');
        const badge = document.querySelector('a[class^="_container_"][class*="_viewerBadge_"]');

        if (profile && profile.style.display !== "none") {
            profile.style.display = 'none';
            console.log("✅ Profilo autore nascosto (interval).");
        }

        if (badge && badge.style.display !== "none") {
            badge.style.display = 'none';
            console.log("✅ Badge Streamlit nascosto (interval).");
        }

        if (profile && badge) {
            console.log("✅ Tutti gli elementi nascosti. Intervallo fermato.");
            clearInterval(interval);
        }
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

