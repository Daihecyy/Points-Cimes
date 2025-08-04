import React, { useCallback, useEffect, useRef, useState } from 'react';
import { View, StyleSheet, PermissionsAndroid, Alert, Pressable, Text, Platform } from 'react-native';
import { MapView, RasterLayer, RasterSource, UserLocation, Camera, UserTrackingMode, MapLibreRNEvent, CameraRef, Location, PointAnnotation, StyleURL } from '@maplibre/maplibre-react-native';
import { IconSymbol } from '../ui/IconSymbol';
import ReportMarker, { ReportType } from './ReportMarker';

const MONT_BLANC_COORDINATES = [6.865575, 45.832119];

// License: https://operations.osmfoundation.org/policies/tiles/
export const OSM_RASTER_STYLE = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "&copy; OpenStreetMap Contributors",
      maxzoom: 19,
    },
  },
  layers: [
    {
      id: "osm",
      type: "raster",
      source: "osm",
    },
  ],
};

function MainMap() {
  const cameraRef = useRef<CameraRef>(null);
  const [isMapLoaded, setIsMapLoaded] = useState<boolean>(false);
  const [userLastLocation, setUserLastLocation] = useState<Location["coords"] | null>(null);
  const [hasLocationPermission, setHasLocationPermission] = useState<boolean>(false);
  const requestLocationPermission = async () => {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        {
          title: 'Location Permission',
          message: 'This app needs access to your location to show you on the map.',
          buttonNeutral: 'Ask Me Later',
          buttonNegative: 'Cancel',
          buttonPositive: 'OK',
        },
      );
      if (granted === PermissionsAndroid.RESULTS.GRANTED) {
        setHasLocationPermission(true);
      } else {
        setHasLocationPermission(false);
        Alert.alert(
          'Permission Denied',
          'Location access is required to show your position on the map. Please enable it in settings.'
        );
      }
    } catch (err) {
      console.warn(err);
      Alert.alert('Error', 'An error occurred while requesting location permission.');
    }
  };
  const onMapDidFinishLoading = () => {
    console.log('Map has finished loading');
    setIsMapLoaded(true);
  };
  const userLocationUpdate = (event: Location) => {
    if (event.coords) {
      setUserLastLocation(event.coords);
    }
  }
  const centerUserLocation = () => {
    if (cameraRef.current && hasLocationPermission && userLastLocation) {
      console.log(userLastLocation)
      cameraRef.current.setCamera({
        pitch: 0,
        centerCoordinate: [userLastLocation.longitude, userLastLocation.latitude],
        zoomLevel: 16,
        animationMode: 'flyTo',
        animationDuration: 1500,
      });
    } else if (!hasLocationPermission) {
      Alert.alert('Permission needed', 'Please grant location access to center the map on your position.');
      requestLocationPermission(); // Prompt for permission again
    }
  };
  useEffect(() => {
    requestLocationPermission();
  }, []);
  const [reports, setReports] = useState([
    {
      id: 'report_1',
      coordinate: [6.866, 45.832] as [number, number],
      title: 'Trail Hazard!',
      description: 'Fallen tree blocking path.',
      type: ReportType.Danger,
    },
    {
      id: 'report_2',
      coordinate: [6.88, 45.91] as [number, number],
      title: 'Beautiful Viewpoint',
      description: 'Stunning panoramic views of Mont Blanc.',
      type: ReportType.Viewpoint,
    },
  ]);
  return (
    <View style={styles.page}>
      <MapView
        style={styles.map}
        onDidFinishLoadingMap={onMapDidFinishLoading}
        localizeLabels={true}
      >
        <RasterSource
          id="osm-raster-source"
          tileUrlTemplates={OSM_RASTER_STYLE.sources.osm.tiles}
          {...OSM_RASTER_STYLE.sources.osm}
        >
          <RasterLayer
            id="osm-raster-layer"
            style={{ rasterOpacity: 1 }}
            belowLayerID="org.maplibre.annotations.points" // IMPORTANT 
          />
        </RasterSource>
        {reports.map((report) => { return <ReportMarker key={report.id} id={report.id} coordinate={report.coordinate} title={report.title} type={report.type} /> })}
        {(hasLocationPermission) &&
          <UserLocation
            minDisplacement={0}
            androidRenderMode="gps"
            onUpdate={userLocationUpdate}
          />
        }
        <Camera
          ref={cameraRef}
          defaultSettings={
            {
              centerCoordinate: MONT_BLANC_COORDINATES,
              zoomLevel: 15,
              animationDuration: 1000,
            }
          }
        />
      </MapView>
      <Pressable onPress={centerUserLocation} style={styles.recenterButton}>
        <IconSymbol name={'location.circle'} color={''} />
      </Pressable>
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
  recenterButton: {
    position: 'absolute', // Position this button absolutely
    bottom: 30,           // 30 logical pixels from the bottom
    right: 20,            // 20 logical pixels from the right
    backgroundColor: '#007bff', // Blue background
    borderRadius: 50,     // Make it a circle
    width: 60,            // Fixed width
    height: 60,           // Fixed height
    justifyContent: 'center', // Center content horizontally
    alignItems: 'center',    // Center content vertically
    elevation: 8,            // Android shadow (for a floating effect)
    shadowColor: '#000',     // iOS shadow
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
  },
  annotationCircle: {
    width: 30,
    height: 30,
    borderRadius: 15, // Makes it a circle
    backgroundColor: 'blue', // Highly visible color
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'white',
  },
  annotationText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
export default MainMap;