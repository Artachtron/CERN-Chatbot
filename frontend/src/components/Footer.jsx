import React from "react";
import { Flex, Input, Button } from "@chakra-ui/react";

const Footer = ({ inputMessage, setInputMessage, handleSendMessage }) => {
    return (
        <Flex w="100%" mt="5">
            <Input
                placeholder="Type Something..."
                border="none"
                rounded="full"
                _focus={{
                    border: "1px solid rgb(51, 102, 255)",
                }}
                onKeyPress={(e) => {
                    if (e.key === "Enter") {
                        handleSendMessage();
                    }
                }}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
            />
            <Button
                color="white"
                rounded="full"
                bg="rgb(51, 102, 255)"
                fontSize='xl'
                p="5"
                _hover={{
                    bg: "white",
                    color: "rgb(51, 102, 255)",
                    border: "1px solid rgb(51, 102, 255)",
                }}
                disabled={inputMessage.trim().length <= 0}
                onClick={handleSendMessage}
            >
                Send
            </Button>
        </Flex >
    );
};

export default Footer;