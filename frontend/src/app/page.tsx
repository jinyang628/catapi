"use client";

import type React from "react";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Message,
  MessagePayload,
  messagePayloadSchema,
  roleEnum,
} from "@/lib/types/messages";
import { sendMessage } from "@/actions/messages";
import StyledMessage from "@/components/shared/markdown-block";

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const currentMessages: Message[] = messages;
    currentMessages.push({
      role: roleEnum.Values.user,
      content: input,
    });
    setMessages(currentMessages);
    setInput("");
    const messageRequestPayload: MessagePayload = messagePayloadSchema.parse({
      message: {
        role: roleEnum.Values.user,
        content: input,
      },
      thread_id: threadId,
    });
    const response = await sendMessage(messageRequestPayload);
    currentMessages.push(response.message);
    setMessages(currentMessages);
    if (!response.thread_id) {
      throw new Error("Thread ID is not returned");
    }
    setThreadId(response.thread_id);
  };

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    setIsTyping(true);
    handleSubmit(e).finally(() => setIsTyping(false));
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Cat Picker</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[60vh] pr-4" ref={scrollAreaRef}>
            {messages.map((m) => (
              <div
                key={`${m.role}-${m.content}-${Math.random().toString(36)}`}
                className={`mb-4 ${m.role === roleEnum.Values.user ? "text-right" : "text-left"}`}
              >
                <StyledMessage role={m.role} content={m.content} />
              </div>
            ))}
            {isTyping && (
              <div className="text-left">
                <span className="inline-block p-2 rounded-lg bg-secondary text-secondary-foreground">
                  Finding the cats...
                </span>
              </div>
            )}
          </ScrollArea>
        </CardContent>
        <CardFooter>
          <form onSubmit={onSubmit} className="flex w-full space-x-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-grow"
            />
            <Button type="submit" disabled={isTyping}>
              Send
            </Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  );
}
