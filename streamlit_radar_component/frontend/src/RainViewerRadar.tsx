import {useEffect, useMemo} from 'react';
import React from 'react'
import { DeckGL } from '@deck.gl/react';
import {TileLayer} from '@deck.gl/geo-layers';
import { BitmapLayer } from '@deck.gl/layers';
import {Streamlit, withStreamlitConnection} from "streamlit-component-lib";


interface Props {
  args: {
    timestamp: number;
    colorscheme: number;
    smoothing: number;
    initialViewState: any;
    height: number;
    satellite: boolean;
    apikey: string
  };
}


const RainviewerRadar = (props: Props) => {
  const {args} = props
  const { timestamp, colorscheme, smoothing, initialViewState, height, satellite, apikey } = args;
  console.log(args)


  console.log(timestamp, colorscheme,smoothing,initialViewState, height)

  const rainLayer = useMemo(() => {
    const tileUrlTemplate = !satellite
        ? `https://tilecache.rainviewer.com/v2/radar/${timestamp}/512/{z}/{x}/{y}/${colorscheme}/${smoothing}_0.png`:
        `https://tilecache.rainviewer.com/v2/satellite/${timestamp}/512/{z}/{x}/{y}/0/0_0.png`;
    console.log("Generating radar")
    return new TileLayer({

      id: 'rainviewer',
      data: [tileUrlTemplate],
      tileSize: 512,
      opacity: 0.5,
      renderSubLayers: (props: any) => {
        const { boundingBox } = props.tile;
        return new BitmapLayer(props, {
            data: undefined,
          image: props.data,
            tile: props.tile,
          bounds: [boundingBox[0][0], boundingBox[0][1], boundingBox[1][0], boundingBox[1][1]],
        });
      },
    });
  }, [timestamp, colorscheme, smoothing]);

  const mapLayer = () => {
    console.log("Generating map layer")
    return new TileLayer({
          id: 'osm-tiles',
          data: 'https://api.maptiler.com/maps/hybrid/{z}/{x}/{y}.jpg?key='+apikey,
          tileSize: 512,
          renderSubLayers: (props: any) => {
            const {boundingBox} = props.tile
            return new BitmapLayer(props, {
                data: undefined,
              image: props.data,
              bounds: [boundingBox[0][0], boundingBox[0][1], boundingBox[1][0], boundingBox[1][1]]
            });
          }
        }
    );
  }

  useEffect(() => {
    // Signal that the component is ready to Streamlit
    Streamlit.setComponentReady();
    Streamlit.setFrameHeight(height); // Ensure correct height adjustment after render
  }, [height]); // Empty dependency array ensures this runs once after the initial render
    console.log(height+"px")
  return (
      <div style={{width: "100%", height: `${height}px`}}>
        <DeckGL
            width="100%"
            height="100%"
            initialViewState={initialViewState}
            controller={true}
            layers={[mapLayer(), rainLayer]}
        />
        <div style={{
          position: "absolute",
          bottom: 4,
          right: 8,
          backgroundColor: "rgba(255,255,255,0.7)",
          padding: "2px 6px",
          fontSize: "10px",
          borderRadius: "4px",
          pointerEvents: "auto"
        }}>
          <a href="https://www.maptiler.com/" target="_blank" rel="noopener noreferrer"
             style={{color: "#000", textDecoration: "none"}}>
            © MapTiler © OpenStreetMap contributors
          </a>
        </div>
      </div>

  );
};

export default withStreamlitConnection(RainviewerRadar);
