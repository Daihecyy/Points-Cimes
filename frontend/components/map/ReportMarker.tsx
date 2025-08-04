import FontAwesomeIcon from "@expo/vector-icons/FontAwesome";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { Callout, PointAnnotation } from "@maplibre/maplibre-react-native";
import { ModalBaseProps, View, Text, StyleSheet } from "react-native";

export enum ReportType {
    Danger,
    Balisage,
    Viewpoint,
}
export interface ReportMarkerProps extends ModalBaseProps {
    id: string,
    coordinate: [number, number],
    title: string,
    type: ReportType
}

export default function ReportMarker({ id, coordinate, title, type, ...props }: ReportMarkerProps) {
    return (
        <>
            <PointAnnotation
                id={id}
                coordinate={coordinate}
                onSelected={() => console.log(id)}
            >
                {
                    {
                        [ReportType.Danger]: <FontAwesomeIcon name={"exclamation-circle"} size={16} color={"red"} />,
                        [ReportType.Viewpoint]: <MaterialIcons name={"landscape"} size={16} />,
                        [ReportType.Balisage]: <MaterialIcons name={"nearby-error"} size={16} />,
                    }[type]
                }
            </PointAnnotation>
        </>
    )
}

const styles = StyleSheet.create({
    annotationCircle: {
        flex: 1,
        width: 50,
        height: 50,
        backgroundColor: 'red',
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 2,
        borderColor: 'white',
    },
    annotationText: {
        color: 'white',
        backgroundColor: 'red',
        fontSize: 24,
        fontWeight: 'bold',
    },
});