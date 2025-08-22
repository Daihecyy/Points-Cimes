import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';
import tw from 'twrnc';


function ButtonGroup({ options, onChange, value }: {
    options: string[];
    onChange: (value: string) => void;
    value: string;
}) {
    return (
        <View style={tw`flex-row justify-around my-2`}>
            {options.map((option) => {
                const isActive = value === option;
                return (
                    <TouchableOpacity
                        key={option}
                        style={tw.style(
                            `py-3 px-5 rounded-full bg-gray-200`,
                            isActive && `bg-blue-500`
                        )}
                        onPress={() => onChange(option)}
                    >
                        <Text style={tw.style(
                            `text-black`,
                            isActive && `text-white font-bold`
                        )}>
                            {option}
                        </Text>
                    </TouchableOpacity>
                );
            })}
        </View>
    );
};

export default ButtonGroup;