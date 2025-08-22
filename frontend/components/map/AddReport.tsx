import { ReportCreation, Reports } from "@/client";
import { client } from "@/client/client.gen";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import {
    Location
} from "@maplibre/maplibre-react-native";
import { PropsWithChildren, useState } from "react";
import { Controller, SubmitHandler, useForm } from "react-hook-form";
import { Alert, Button, Modal, Pressable, Text, TextInput, View } from "react-native";
import tw from 'twrnc';
import ButtonGroup from "../ui/ButtonGroup";
import LocationSelector from "./LocationSelector";

interface AddReportProps extends PropsWithChildren {
    userLocation: Location["coords"] | null;
    startingLocation: [number, number];
}

function AddReport({ startingLocation, userLocation }: AddReportProps) {
    const [modalVisible, setModalVisible] = useState(false);
    const {
        control,
        handleSubmit,
        formState: { errors },
    } = useForm<ReportCreation>();
    const onSubmit: SubmitHandler<ReportCreation> = async (formData) => {
        const { data, error } = await Reports.postReports({
            client: client,
            body: {
                title: formData.title,
                report_type: formData.report_type,
                description: formData.description,
                location: formData.location,

            }
        });
        if (error) {
            console.log(error);
            Alert.alert(
                "Error",
                "Erreur en soumettant la requete",
            );
            return;
        }
        setModalVisible(false);
    };
    return (
        <View style={tw``}>
            <Pressable
                style={tw``}
                onPress={() => setModalVisible(!modalVisible)}
            >
                <MaterialIcons name={"add"} size={24} />
            </Pressable>
            <Modal
                visible={modalVisible}
                onRequestClose={() => {
                    setModalVisible(!modalVisible);
                }}
            >
                <View style={tw`flex-1 pb-2`}>
                    <Pressable
                        style={tw`self-end p-1`}
                        onPress={() => setModalVisible(false)}
                    >
                        <MaterialIcons name={"close"} size={36} />
                    </Pressable>
                    <View style={tw`flex-1 p-2`}>
                        <View>
                            <Text>Titre</Text>
                            <Controller
                                control={control}
                                name="title"
                                rules={{ required: true }}
                                render={({ field: { onChange, value } }) => (
                                    <TextInput
                                        style={{ borderWidth: 1, marginBottom: 10 }}
                                        onChangeText={onChange}
                                        value={value}
                                    />
                                )}
                            />
                            {errors.title && <Text>This field is required.</Text>}
                        </View>
                        <View>
                            <Text>Type</Text>
                            <Controller
                                control={control}
                                name="report_type"
                                rules={{ required: true }}
                                render={({ field: { onChange, value } }) => (
                                    <ButtonGroup options={["highlight", "danger", "problem"]} onChange={onChange} value={value} />
                                )}
                            />
                            {errors.report_type && <Text>This field is required.</Text>}
                        </View>
                        <View>
                            <Text>Description</Text>
                            <Controller
                                control={control}
                                name="description"
                                render={({ field: { onChange, value } }) => (
                                    <TextInput
                                        style={{ borderWidth: 1, marginBottom: 10 }}
                                        onChangeText={onChange}
                                        value={value}
                                    />
                                )}
                            />
                        </View>
                        <View style={tw`flex-1`}>
                            <Text>Location</Text>
                            <Controller
                                control={control}
                                name="location"
                                rules={{ required: true }}
                                render={({ field: { onChange, value } }) => (
                                    <LocationSelector userLocation={userLocation} startingLocation={startingLocation} setChosenLocation={onChange} chosenLocation={value} />
                                )}
                            />
                        </View>
                    </View>
                    <Button title="Submit" onPress={handleSubmit(onSubmit)} />
                </View>
            </Modal>
        </View>
    )
};
export default AddReport;