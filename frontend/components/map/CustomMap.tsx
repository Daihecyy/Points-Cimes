import {
	Camera,
	CameraRef,
	MapView,
	RasterLayer,
	RasterSource,
	RegionPayload
} from "@maplibre/maplibre-react-native";
import React, { PropsWithChildren, RefObject } from "react";
import {
	View
} from "react-native";
import tw, { Style } from "twrnc";


interface CustomMapProps extends PropsWithChildren {
	cameraRef: RefObject<CameraRef | null>;
	setIsMapLoaded?: (isMapLoaded: boolean) => void;
	setCurrentZoomLevel?: (currentZoomLevel: number) => void;
	startingCenter: [number, number];
	setMapCenter?: (mapCenter: number[]) => void;
	style?: Style;
}

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

function CustomMap({ cameraRef, setIsMapLoaded, setCurrentZoomLevel, startingCenter, children, setMapCenter, style }: CustomMapProps) {
	const onMapDidFinishLoading = () => {
		if (setIsMapLoaded) {
			setIsMapLoaded(true);
		}
	};
	const handleCameraChanged = (
		feature: GeoJSON.Feature<GeoJSON.Point, RegionPayload>,
	) => {
		// WARNING : Watch for performance impact
		if (setCurrentZoomLevel && feature.properties.zoomLevel) {
			setCurrentZoomLevel(feature.properties.zoomLevel);
		}
		if (setMapCenter && feature.geometry.coordinates) {
			setMapCenter(feature.geometry.coordinates)
		}
	};
	return (
		<View style={tw.style("flex-1", style)}>
			<MapView
				style={tw`flex-1`}
				onDidFinishLoadingMap={onMapDidFinishLoading}
				onRegionIsChanging={handleCameraChanged}
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
				<Camera
					ref={cameraRef}
					defaultSettings={{
						centerCoordinate: startingCenter,
						zoomLevel: 15,
						animationDuration: 1000,
					}}
				/>
				{children}
			</MapView>
		</View>
	);
}

export default CustomMap;
