import React, { useEffect, useRef } from "react";
import { Avatar, Flex, Text } from "@chakra-ui/react";

const Messages = ({ messages }) => {
    const AlwaysScrollToBottom = () => {
        const elementRef = useRef();
        useEffect(() => elementRef.current.scrollIntoView());
        return <div ref={elementRef} />;
    };

    return (
        <Flex w="100%" h="80%" overflowY="scroll" flexDirection="column" p="3">
            {messages.map((item, index) => {
                if (item.from === "me") {
                    return (
                        <Flex key={index} w="100%" justify="flex-end">
                            <Flex
                                bg="rgb(51, 102, 255)"
                                color="white"
                                minW="100px"
                                maxW="350px"
                                my="1"
                                p="3"
                                rounded="full" // Modify rounded property to "full" for a more rounded shape
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
                                bg="gray.100"
                                color="black"
                                minW="100px"
                                maxW="350px"
                                my="1"
                                p="3"
                                rounded="full"
                            >
                                <Text>{item.text}</Text>
                            </Flex>
                        </Flex>
                    );
                }
            })}
            <AlwaysScrollToBottom />
        </Flex>
    );
};

export default Messages;