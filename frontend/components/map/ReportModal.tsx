import { Report } from "@/client";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { PropsWithChildren } from "react";
import { Modal, Pressable, Text, View } from "react-native";
import tw from 'twrnc';

interface ReportModalProps extends PropsWithChildren {
    report: Report;
    modalVisible: boolean;
    setModalVisible: (modalVisible: boolean) => void;
}

function ReportModal({ report, modalVisible, setModalVisible }: ReportModalProps) {
    const handleVote = (voteValue: string) => {
        console.log(voteValue);
    }
    return (
        <Modal
            visible={modalVisible}
            onRequestClose={() => {
                setModalVisible(!modalVisible);
            }}
            style={tw`flex p-4`}
        >
            <Pressable
                style={tw`self-end p-1`}
                onPress={() => setModalVisible(false)}
            >
                <MaterialIcons name={"close"} size={36} />
            </Pressable>
            <View style={tw`flex-1 p-2`}>
                <Text style={tw`text-xl`}>{report.title}</Text>
                <Text style={tw`text-lg`}>{report.report_type}</Text>
                {(report.description !== "") && <Text>{report.description}</Text>}
                <View style={tw`flex w-fit flex-row gap-2 border-2 rounded-lg`}>
                    <Pressable
                        style={tw`p-1`}
                        onPress={() => handleVote("down")}
                    >
                        <MaterialIcons name={"thumb-up"} size={24} />
                    </Pressable>
                    <Pressable
                        style={tw`p-1`}
                        onPress={() => handleVote("up")}
                    >
                        <MaterialIcons name={"thumb-down"} size={24} />
                    </Pressable>
                </View>
            </View>
        </Modal>
    )
};
export default ReportModal;