import React, { useEffect, useRef, useState } from 'react';
import { View, StyleSheet, PermissionsAndroid, Alert, Pressable } from 'react-native';
import { MapView, RasterLayer, RasterSource, UserLocation, Camera, UserTrackingMode, MapLibreRNEvent, CameraRef } from '@maplibre/maplibre-react-native';
import { IconSymbol } from '../ui/IconSymbol';

function MainMap() {
  const cameraRef = useRef<CameraRef>(null);
  const [isFollowingUser, setIsFollowingUser] = useState<boolean>(false);
  const [isMapLoaded, setIsMapLoaded] = useState<boolean>(false);
  const [hasLocationPermission, setHasLocationPermission] = useState<boolean>(false);
  const requestLocationPermission = async () => {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION, // Request fine location for better accuracy
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
    if (hasLocationPermission) {
      setIsFollowingUser(true);
    }
  };
  const onCenterUserLocation = () => {
    if (cameraRef.current && hasLocationPermission) {
      cameraRef.current.setCamera({
        zoomLevel: 15,
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
  return (
    <View style={styles.page}>
      <MapView
        style={styles.map}
        onDidFinishLoadingMap={onMapDidFinishLoading}
        localizeLabels={true}
      >
        <RasterSource
          id="osmRasterSource"
          tileUrlTemplates={['https://tile.openstreetmap.org/{z}/{x}/{y}.png']}
          tileSize={256} // OSM tiles are 256x256 pixels
          maxZoomLevel={19} // Max zoom level supported by OSM tiles
          attribution="© OpenStreetMap contributors" // Essential for legal compliance!
        >
          <RasterLayer
            id="osmRasterLayer"
            sourceID="osmRasterSource"
          />
        </RasterSource>
        {(hasLocationPermission) &&
          <UserLocation
            minDisplacement={2}
            androidRenderMode="gps"
          />
        }
        <Camera
          ref={cameraRef}
          followUserLocation={hasLocationPermission && isFollowingUser}
          followUserMode={UserTrackingMode.FollowWithCourse}
          followZoomLevel={15}
          animationMode="flyTo"
          animationDuration={1000} // Duration of the animation
        />
      </MapView>
      <Pressable onPress={onCenterUserLocation} style={styles.recenterButton}>
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
});

export default MainMap;