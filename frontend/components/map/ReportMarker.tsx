import { ReportType } from "@/client";
import FontAwesomeIcon from "@expo/vector-icons/FontAwesome";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { PointAnnotation } from "@maplibre/maplibre-react-native";
import { ModalBaseProps } from "react-native";

export interface ReportMarkerProps extends ModalBaseProps {
    id: string,
    coordinate: [number, number],
    title: string,
    type: ReportType
    handlePress: () => void;
}

export default function ReportMarker({ id, coordinate, title, type, handlePress, ...props }: ReportMarkerProps) {
    return (
        <PointAnnotation
            id={id}
            coordinate={coordinate}
            onSelected={() => { console.log(id); handlePress(); }}
        >
            {
                {
                    ["danger"]: <FontAwesomeIcon name={"exclamation-circle"} size={24} color={"red"} />,
                    ["highlight"]: <MaterialIcons name={"landscape"} size={24} />,
                    ["problem"]: <MaterialIcons name={"nearby-error"} size={24} />,
                }[type]
            }
        </PointAnnotation>
    )
}
