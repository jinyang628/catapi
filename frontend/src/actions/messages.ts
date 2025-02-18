"use server";

import { MessagePayload, messagePayloadSchema } from "@/lib/types/messages";
import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const MESSAGES_SERVICE_ENDPOINT = "api/messages";

export async function sendMessage(
  input: MessagePayload,
): Promise<MessagePayload> {
  try {
    console.log("Sending, input: ", input);
    const response = await axios.post(
      `${BASE_URL}/${MESSAGES_SERVICE_ENDPOINT}`,
      input,
    );
    const messageResponse: MessagePayload = messagePayloadSchema.parse(
      response.data,
    );

    return messageResponse;
  } catch (error: unknown) {
    console.error(`Error sending message: ${error}`);
    throw error;
  }
}
