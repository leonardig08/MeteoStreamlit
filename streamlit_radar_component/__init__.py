import os
import streamlit.components.v1 as components

import streamlit as st
import requests

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("streamlit_radar_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "rainviewer_radar",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to the component's
    # build directory:
    build_dir = os.path.dirname(os.path.realpath(__file__))+"/frontend/build"
    _component_func = components.declare_component("rainviewer_radar", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def rainviewer_radar(timestamp: int, colorscheme: int = 7, smoothing: int = 1, initial_view_state=None, key=None, height=300, satellite=False, apikey:str = ""):
    """Visualizza il TileLayer radar di Rainviewer con deck.gl."""
    return _component_func(
        timestamp=timestamp,
        colorscheme=colorscheme,
        smoothing=smoothing,
        initialViewState=initial_view_state if initial_view_state is not None else {
            "latitude": 45.5,
            "longitude": 15.3,
            "zoom": 4,
        },
        key=key,
        height=height,
        satellite=satellite,
        apikey=apikey,
    )

if __name__ == "__main__":
    @st.cache_data(ttl=300)  # Cache per 5 minuti per non sovraccaricare l'API
    def get_rainviewer_timestamps():
        try:
            response = requests.get("https://api.rainviewer.com/public/weather-maps.json")
            data = response.json()
            dataparsed = data.get('radar', {}).get('past', [])
            datareturn = [i["time"] for i in dataparsed]
            return datareturn
        except requests.exceptions.RequestException as e:
            st.error(f"Errore nel recupero dei timestamp da Rainviewer: {e}")
            return []
    st.set_page_config(layout="wide")

    # ⏱️ SLIDER per scegliere il timestamp (simulato o reale)
    current_timestamp = st.select_slider(
        "Seleziona Timestamp Rainviewer",
        options=get_rainviewer_timestamps(),
    )

    st.write(f"🕒 Timestamp selezionato: {current_timestamp}")

    # Mostra il componente
    rainviewer_radar(
        timestamp=current_timestamp,
        colorscheme=7,
        smoothing=1,
        key="rainviewer"
    )
