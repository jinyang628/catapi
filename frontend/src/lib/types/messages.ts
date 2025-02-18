import { z } from "zod";

export const roleEnum = z.enum(["user", "assistant"]);

export const messageSchema = z.object({
  role: roleEnum,
  content: z.string(),
});

export type Message = z.infer<typeof messageSchema>;

export const messagePayloadSchema = z.object({
  thread_id: z.string().nullable(),
  message: messageSchema,
});

export type MessagePayload = z.infer<typeof messagePayloadSchema>;
