import React from "react";
import { Flex, Avatar, AvatarBadge, Text } from "@chakra-ui/react";

const Header = () => {
    return (
        <Flex w="100%">
            <Avatar size="lg" name="Florent Vaucher" src="https://cdn2.psychologytoday.com/assets/styles/manual_crop_1_1_288x288/public/teaser_image/blog_entry/2023-11/epictetus%20copy.jpg?itok=l_8ZctKe">
                <AvatarBadge boxSize="1.25em" bg="green.500" border="1px solid black" />
            </Avatar>
            <Flex flexDirection="column" mx="5" justify="center">
                <Text fontSize="lg" fontWeight="bold">
                    Florent Vaucher
                </Text>
                <Text color="green.500">Online</Text>
            </Flex>
        </Flex>
    );
};

export default Header;