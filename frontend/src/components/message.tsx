import React from "react";
import { Avatar, Box, Card, CardContent, Typography } from "@mui/material";
export type MessageProps = {
  username: string;
  text: string;
};

function Message({ text, username }: MessageProps) {
  const getUserAvatar = (username: string) => {
    if (username === "Human") {
      return "https://cdn2.psychologytoday.com/assets/styles/manual_crop_1_1_288x288/public/teaser_image/blog_entry/2023-11/epictetus%20copy.jpg?itok=l_8ZctKe";
    } else if (username === "Bot") {
      return "https://upload.wikimedia.org/wikipedia/en/thumb/a/ae/CERN_logo.svg/640px-CERN_logo.svg.png";
    }
  };

  const isHuman = username === "Human";

  return (
    <div className={`flex ${isHuman ? "justify-end" : "justify-start"} mb-2`}>
      <div
        className={`flex ${
          isHuman ? "flex-row-reverse" : "flex-row"
        } items-center`}
      >
        <Avatar src={getUserAvatar(username)} className="w-12 h-12 " />
        <CardContent
          style={{ paddingBottom: 12 }}
          className={`pt-3 pb-0 rounded-lg max-w-[500px] ${
            isHuman ? "bg-green-500 text-white" : "bg-blue-500 text-white"
          }`}
        >
          <Typography variant="body1" className="text-sm">
            {text}
          </Typography>
        </CardContent>
      </div>
    </div>
  );
}

export default Message;
