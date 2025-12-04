import { GoogleGenAI, GenerateContentResponse } from "@google/genai";

// Initialize the client
// Note: In a real scenario, ensure process.env.API_KEY is set.
// For this demo, we will gracefully handle missing keys by throwing identifiable errors
// that the UI can catch to show "Simulation Mode" or fallback responses.

const apiKey = process.env.API_KEY || '';

let ai: GoogleGenAI | null = null;

if (apiKey) {
  ai = new GoogleGenAI({ apiKey });
}

export const sendMessageToGemini = async (
  history: { role: 'user' | 'model'; text: string }[],
  newMessage: string
): Promise<string> => {
  if (!ai) {
    console.warn("Gemini API Key missing. Returning mock response.");
    // Simulate a network delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    return "I'm currently running in demo mode because no API Key was detected. I can help you simulate adding events to your calendar!";
  }

  try {
    const model = 'gemini-2.5-flash'; 
    
    // Construct prompt with history context
    // In a real app, we would use ai.chats.create for true history management,
    // but for a stateless request wrapper, we can format the prompt.
    
    // However, let's use the Chat API for best practice if we were persisting the session object.
    // Since this function is stateless, we'll re-create a chat session or just send the full prompt.
    // For simplicity in this helper:
    
    const chat = ai.chats.create({
      model: model,
      config: {
        systemInstruction: "You are a helpful AI scheduler assistant. You help users manage their calendar. Keep responses concise and friendly.",
      },
      history: history.map(h => ({
        role: h.role,
        parts: [{ text: h.text }]
      }))
    });

    const result: GenerateContentResponse = await chat.sendMessage({
      message: newMessage
    });

    return result.text || "I didn't understand that.";

  } catch (error) {
    console.error("Error calling Gemini API:", error);
    return "Sorry, I encountered an error processing your request.";
  }
};
