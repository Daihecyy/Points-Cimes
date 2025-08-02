import { Callout, PointAnnotation } from "@maplibre/maplibre-react-native";
import { ModalBaseProps, View, Text, StyleSheet } from "react-native";

export enum ReportType {
    Danger,
    Balisage,
    POV,
}
export interface ReportMarkerProps extends ModalBaseProps {
    id: string,
    coordinate: [number, number],
    title: string,
    type: string
}

export default function ReportMarker({ id, coordinate, title, type, ...props }: ReportMarkerProps) {
    return (
        <>
            <PointAnnotation
                id={id}
                coordinate={coordinate}
                onSelected={() => console.log(id)}
            >
                <View style={styles.annotationCircle}>
                    <Text style={styles.annotationText}>{type === 'hazard' ? '!' : 'V'}</Text>
                </View>
                <Callout title={title} />
            </PointAnnotation>
        </>
    )
}

const styles = StyleSheet.create({
    annotationCircle: {
        width: 50,
        height: 50,
        borderRadius: 15, // Makes it a circle
        backgroundColor: 'red', // Highly visible color
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 2,
        borderColor: 'white',
    },
    annotationText: {
        color: 'white',
        fontSize: 24,
        fontWeight: 'bold',
    },
});