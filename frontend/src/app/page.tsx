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

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setInput("");
    const messageRequestPayload: MessagePayload = messagePayloadSchema.parse({
      message: {
        role: roleEnum.Values.user,
        content: input,
      },
      thread_id: threadId,
    });
    const response = await sendMessage(messageRequestPayload);
    setMessages((prev) => [...prev, response.message]);
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
          <CardTitle>Chat Interface</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[60vh] pr-4" ref={scrollAreaRef}>
            {messages.map((m) => (
              <div
                key={`${m.role}-${m.content}-${Math.random().toString(36)}`}
                className={`mb-4 ${m.role === roleEnum.Values.user ? "text-right" : "text-left"}`}
              >
                <span
                  className={`inline-block p-2 rounded-lg ${m.role === roleEnum.Values.user ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"}`}
                >
                  {m.content}
                </span>
              </div>
            ))}
            {isTyping && (
              <div className="text-left">
                <span className="inline-block p-2 rounded-lg bg-secondary text-secondary-foreground">
                  Bot is typing...
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
