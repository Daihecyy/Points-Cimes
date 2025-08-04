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
    )
}
