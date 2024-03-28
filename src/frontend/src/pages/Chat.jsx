import { Flex } from "@chakra-ui/react";
import React, { useState } from "react";
import Divider from "../components/Divider";
import Footer from "../components/Footer";
import Header from "../components/Header";
import Messages from "../components/Messages";

const Chat = () => {
    const [messages, setMessages] = useState([
        { from: "computer", text: "Hi, My Name is CERN Bot" },
        { from: "me", text: "Hey there" },
        { from: "me", text: "Myself Florent Vaucher" },
        {
            from: "computer",
            text: "Nice to meet you. You can send me message and i'll reply you with same message.",
        },
    ]);
    const [inputMessage, setInputMessage] = useState("");

    const handleSendMessage = async () => {
        if (!inputMessage.trim().length) {
            return;
        }

        setMessages((old) => [...old, { from: "me", text: inputMessage }]);
        setInputMessage("");

        const response = await fetch("http://localhost:8000/chat/question", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: inputMessage })
        });

        const data = await response.json();
        console.log(data);

        setTimeout(() => {
            setMessages((old) => [...old, { from: "computer", text: data.answer }]);
        }, 1000);
    };

    return (
        <Flex w="100%" h="100vh" justify="center" align="center">
            <Flex w="40%" h="90%" flexDir="column">
                <Header />
                <Divider />
                <Messages messages={messages} />
                <Divider />
                <Footer
                    inputMessage={inputMessage}
                    setInputMessage={setInputMessage}
                    handleSendMessage={handleSendMessage}
                />
            </Flex>
        </Flex>
    );
};

export default Chat;