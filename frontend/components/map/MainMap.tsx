import { Report, Reports } from "@/client";
import { client } from "@/client/client.gen";
import useLocationPermission from "@/hooks/useLocationPermission";
import {
	CameraRef,
	Location,
	RegionPayload,
	UserLocation
} from "@maplibre/maplibre-react-native";
import React, { useEffect, useRef, useState } from "react";
import {
	Alert,
	Pressable,
	StyleSheet,
	View
} from "react-native";
import { IconSymbol } from "../ui/IconSymbol";
import AddReport from "./AddReport";
import CustomMap from "./CustomMap";
import ReportMarker from "./ReportMarker";

const MONT_BLANC_COORDINATES = [6.865575, 45.832119] as [number, number];
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
	const { hasLocationPermission, requestLocationPermission } = useLocationPermission();
	const [reports, setReports] = useState<Report[]>([]);
	const [currentZoomLevel, setCurrentZoomLevel] = useState<number>(15);
	const [userLastLocation, setUserLastLocation] = useState<
		Location["coords"] | null
	>(null);

	const onGetReportsById = async (reportId: string) => {
		console.log("fired");
		const { data, error } = await Reports.getReportsReportId({
			client: client,
			path: {
				report_id: reportId,
			},
		});
		if (error) {
			console.log(error);
			console.log("err")
			return;
		}
		console.log(data)
		setReports([data!]);
	};
	const userLocationUpdate = (event: Location) => {
		if (event.coords) {
			setUserLastLocation(event.coords);
		}
	};

	const centerUserLocation = () => {
		if (cameraRef.current && hasLocationPermission && userLastLocation) {
			cameraRef.current.setCamera({
				pitch: 0,
				centerCoordinate: [
					userLastLocation.latitude,
					userLastLocation.longitude,
				],
				zoomLevel: 16,
				animationMode: "flyTo",
				animationDuration: 1500,
			});
		} else if (!hasLocationPermission) {
			Alert.alert(
				"Permission needed",
				"Please grant location access to center the map on your position.",
			);
			requestLocationPermission(); // Prompt for permission again
		}
	};

	const handleCameraChanged = (
		feature: GeoJSON.Feature<GeoJSON.Point, RegionPayload>,
	) => {
		// WARNING : Watch for performance impact
		if (feature.properties.zoomLevel) {
			setCurrentZoomLevel(feature.properties.zoomLevel);
		}
	};
	useEffect(() => {
		requestLocationPermission();
		onGetReportsById("a6f8f86c-7ee0-4519-826d-7588f2ea0f4b");
	}, []);
	return (
		<View style={styles.page}>
			<CustomMap cameraRef={cameraRef} setIsMapLoaded={setIsMapLoaded} setCurrentZoomLevel={setCurrentZoomLevel} startingCenter={MONT_BLANC_COORDINATES} >
				{currentZoomLevel > 1 &&
					reports.map((report) => {
						return (
							<ReportMarker
								key={report.id}
								id={report.id}
								coordinate={[report.longitude, report.latitude]}
								title={report.title}
								type={report.report_type}
							/>
						);
					})}
				{hasLocationPermission && (
					<UserLocation
						minDisplacement={0}
						androidRenderMode="gps"
						onUpdate={userLocationUpdate}
					/>
				)}
			</CustomMap>
			<Pressable onPress={centerUserLocation} style={styles.recenterButton}>
				<IconSymbol name={"location.circle"} color={""} />
			</Pressable>
			<AddReport></AddReport>
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
		position: "absolute", // Position this button absolutely
		bottom: 30, // 30 logical pixels from the bottom
		right: 20, // 20 logical pixels from the right
		backgroundColor: "#007bff", // Blue background
		borderRadius: 50, // Make it a circle
		width: 60, // Fixed width
		height: 60, // Fixed height
		justifyContent: "center", // Center content horizontally
		alignItems: "center", // Center content vertically
		elevation: 8, // Android shadow (for a floating effect)
		shadowColor: "#000", // iOS shadow
		shadowOffset: { width: 0, height: 4 },
		shadowOpacity: 0.3,
		shadowRadius: 5,
	},
	annotationCircle: {
		width: 30,
		height: 30,
		borderRadius: 15, // Makes it a circle
		backgroundColor: "blue", // Highly visible color
		justifyContent: "center",
		alignItems: "center",
		borderWidth: 2,
		borderColor: "white",
	},
	annotationText: {
		color: "white",
		fontSize: 18,
		fontWeight: "bold",
	},
});
export default MainMap;
