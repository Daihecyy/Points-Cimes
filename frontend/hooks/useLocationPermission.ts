import { useCallback, useEffect, useState } from 'react';
import { Alert, PermissionsAndroid } from 'react-native';

const useLocationPermission = () => {
  const [hasLocationPermission, setHasLocationPermission] =
    useState<boolean>(false);
  const requestLocationPermission = useCallback(async () => {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        {
          title: "Location Permission",
          message:
            "This app needs access to your location to show you on the map.",
          buttonNeutral: "Ask Me Later",
          buttonNegative: "Cancel",
          buttonPositive: "OK",
        },
      );
      if (granted === PermissionsAndroid.RESULTS.GRANTED) {
        setHasLocationPermission(true);
      } else {
        setHasLocationPermission(false);
        Alert.alert(
          "Permission Denied",
          "Location access is required to show your position on the map. Please enable it in settings.",
        );
      }
    } catch (err) {
      console.warn(err);
      Alert.alert(
        "Error",
        "An error occurred while requesting location permission.",
      );
    }
  }, []);

  useEffect(() => {
    requestLocationPermission();
  }, [requestLocationPermission]);

  return {hasLocationPermission, requestLocationPermission};
}

export default useLocationPermission;