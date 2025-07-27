import React from 'react';
import { View, StyleSheet } from 'react-native';
import {MapView, RasterLayer, RasterSource, UserLocation } from '@maplibre/maplibre-react-native';

// Optional: Set a default access token if required by the SDK for initialization.
// MapLibre GL Native SDKs generally don't require an access token for most uses,
// but some older versions or specific configurations might.
// If you encounter issues, try setting a dummy token or removing this line.
// MapLibreGL.setAccessToken('pk.YOUR_DUMMY_TOKEN_OR_REMOVE_ME'); 

function MainMap() {
  return (
    <View style={styles.page}>
      <MapView
        style={styles.map}
        // OR, if you prefer a very basic dark/light empty style:
        // styleURL='https://demotiles.maplibre.org/style.json'
        // This public style is for demo purposes and might not be suitable for production.
        // It provides basic streets but you'd need to check its source.
        
        // Initial camera position (e.g., somewhere in France)
        // camera={{
        //   centerCoordinate: [2.3522, 48.8566], // Paris coordinates (lon, lat)
        //   zoomLevel: 9,
        //   animationDuration: 0,
        // }}
      >
        {/* Define a RasterSource for OpenStreetMap tiles */}
        <RasterSource
          id="osmRasterSource"
          tileUrlTemplates={['https://tile.openstreetmap.org/{z}/{x}/{y}.png']}
          tileSize={256} // OSM tiles are 256x256 pixels
          maxZoomLevel={19} // Max zoom level supported by OSM tiles
          attribution="© OpenStreetMap contributors" // Essential for legal compliance!
        >
          {/* Add a RasterLayer to display the tiles from the source */}
          <RasterLayer
            id="osmRasterLayer"
            sourceID="osmRasterSource"
            // Optional: Adjust opacity if you want to overlay other layers
            style={{
              rasterOpacity: 1,
            }}
          />
        </RasterSource>

        {/* You can add other layers (e.g., GeoJSON for trails, markers) here */}
        {/* <MapLibreGL.ShapeSource id="trails" url="http://your-backend/trails.geojson">
          <MapLibreGL.LineLayer id="trailLines" style={{ lineColor: 'blue', lineWidth: 2 }} />
        </MapboxGL.ShapeSource> */}

      </MapView>
    </View>
  );
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
});

export default MainMap;