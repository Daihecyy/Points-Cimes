import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import {
    CameraRef,
    Location
} from "@maplibre/maplibre-react-native";
import React, { PropsWithChildren, useEffect, useRef, useState } from 'react';
import { Switch, Text, View } from 'react-native';
import tw from "twrnc";
import CustomMap from './CustomMap';

interface LocationSelectorProps extends PropsWithChildren {
    userLocation: Location["coords"] | null;
    startingLocation: [number, number];
    chosenLocation: string
    setChosenLocation: (chosenLocation: string) => void;
}

const DECIMAL_PRECISION = 5;

function LocationSelector({ userLocation, setChosenLocation, startingLocation, chosenLocation }: LocationSelectorProps) {
    const [usingMyLoc, setUsingMyLoc] = useState<boolean>((userLocation == null));
    const toogleMyLocSwitch = () => setUsingMyLoc(!usingMyLoc);
    const cameraRef = useRef<CameraRef>(null);
    const [mapCenter, setMapCenter] = useState<number[]>();
    useEffect(() => {
        let newLocationText = "";
        if (!usingMyLoc && userLocation) {
            newLocationText = `POINT(${userLocation.longitude.toFixed(DECIMAL_PRECISION)}, ${userLocation.latitude.toFixed(DECIMAL_PRECISION)})`;
        } else if (mapCenter) {
            newLocationText = `POINT(${mapCenter[0].toFixed(DECIMAL_PRECISION)} ${mapCenter[1].toFixed(DECIMAL_PRECISION)})`;
        }
        setChosenLocation(newLocationText);
    }, [usingMyLoc, userLocation, mapCenter]);
    return (
        <View style={tw`flex-1`}>
            <View style={tw`flex-1`}>
                <Switch value={usingMyLoc} onValueChange={toogleMyLocSwitch} />
                <Text>{usingMyLoc ? "Choisir sur la carte" : "My localisation"}</Text>
                <Text> Selected Location: {chosenLocation}</Text>
                {usingMyLoc &&
                    <View style={tw`relative p-2 aspect-square w-full`}>
                        <CustomMap style={tw`border-4 rounded-sm`} cameraRef={cameraRef} startingCenter={startingLocation} setMapCenter={setMapCenter} />
                        <View style={tw`flex absolute top-[50%] left-[50%]`}>
                            <MaterialIcons name={"add"} size={36} />
                        </View>
                    </View>
                }
            </View >
        </View>
    );
};

export default LocationSelector;