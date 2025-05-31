import streamlit as st
import pytz
import requests
import streamlit.components.v1 as components


hide_css = """
<script>
function hideProfile() {
    const profile = document.querySelector('div[class^="_profileContainer_"]');
    if (profile && profile.style.display !== "none") {
        profile.style.display = "none";
        console.log("Profilo nascosto");
    }
}

const interval = setInterval(() => {
    try {
        hideProfile();

        if (window.top && window.top.document) {
            window.top.document.querySelectorAll(`[href*="streamlit.io"]`).forEach(e => {
                if (e.style.display !== "none") {
                    e.style.display = "none";
                    console.log("Link streamlit.io nascosto (top window)");
                }
            });
        }
    } catch(e) {
        console.warn("Errore accesso window.top.document:", e);
        clearInterval(interval); // stop se non ha accesso per non spam
    }
}, 1000);
</script>
"""



testscript = '<script>console.log("TEST")</script>'




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
    st.markdown(hide_css, unsafe_allow_html=True)
    components.html(hide_css)

