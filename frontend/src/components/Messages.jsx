import React, { useEffect, useRef } from "react";
import { Avatar, Flex, Text, Box } from "@chakra-ui/react";

const Messages = ({ messages }) => {
    const AlwaysScrollToBottom = () => {
        const elementRef = useRef();
        useEffect(() => elementRef.current.scrollIntoView());
        return <div ref={elementRef} />;
    };

    return (

        <Flex w="100%" h="80%" overflowY="scroll" flexDirection="column">
            <Box h="20px"></Box>
            <Flex w="100%" h="80%" flexDirection="column" p="3">


                {messages.map((item, index) => {
                    if (item.from === "me") {
                        return (
                            <Flex key={index} w="100%" justify="flex-end">

                                <Flex
                                    // bg="rgb(51, 102, 255)"
                                    color="user.color"
                                    bg="user.bg"

                                    // border="1px solid"
                                    // borderColor="brand.userColor"
                                    minW="100px"
                                    maxW="350px"
                                    my="1"
                                    mr="2"
                                    p="3"
                                    rounded="md"
                                >
                                    <Text>{item.text}</Text>
                                </Flex>
                                <Avatar
                                    name="Florent Vaucher"
                                    src="https://cdn2.psychologytoday.com/assets/styles/manual_crop_1_1_288x288/public/teaser_image/blog_entry/2023-11/epictetus%20copy.jpg?itok=l_8ZctKe"
                                >
                                </Avatar>
                            </Flex>
                        );
                    } else {
                        return (
                            <Flex key={index} w="100%">
                                <Avatar
                                    name="Computer"
                                    src="https://upload.wikimedia.org/wikipedia/en/thumb/a/ae/CERN_logo.svg/640px-CERN_logo.svg.png"
                                    bg="blue.300"
                                ></Avatar>
                                <Flex

                                    bg="brand.bg"
                                    color="brand.color"
                                    minW="100px"
                                    maxW="350px"
                                    my="1"
                                    p="3"
                                    ml="2"
                                    rounded="md"
                                >
                                    <Text>{item.text}</Text>
                                </Flex>
                            </Flex>
                        );
                    }
                })}
                <AlwaysScrollToBottom />
            </Flex>
        </Flex>
    );
};

export default Messages;