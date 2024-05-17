"use client";

import React, { useState } from "react";
import { Card, CardContent, TextField, Button } from "@mui/material";
import Message, { MessageProps } from "./message";
import { BASE_URL } from "@/utils/backend";

function Chat() {
  const [messages, setMessages] = useState<MessageProps[]>([]);

  const [message, setMessage] = useState("");
  const [isBotTyping, setIsBotTyping] = useState(false);

  const handleSubmit = async (
    event: React.MouseEvent<HTMLButtonElement, MouseEvent>
  ) => {
    event.preventDefault();
    if (!message.trim().length) return;

    setIsBotTyping(true);

    setMessages([...messages, { username: "Human", text: message }]);
    setMessage("");

    const response = await fetch(`${BASE_URL}/chat/question`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: message }),
    });

    const data = await response.json();
    console.log(data);

    setTimeout(() => {
      setMessages((old) => [...old, { username: "Bot", text: data.answer }]);
    }, 1000);
  };

  const handleChangeMessage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(event.target.value);
  };

  return (
    <Card>
      <CardContent>
        <div className="h-[400px] overflow-auto mb-4">
          {messages.map((message, index) => (
            <Message
              key={index}
              text={message.text}
              username={message.username}
            />
          ))}
        </div>
        <form>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type a message"
            className="mb-4"
            value={message}
            onChange={handleChangeMessage}
          />
          <Button
            variant="contained"
            color="primary"
            type="submit"
            onClick={handleSubmit}
            disabled={isBotTyping}
          >
            Send
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

export default Chat;
