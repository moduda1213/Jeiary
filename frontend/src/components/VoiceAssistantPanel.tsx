import { useState } from "react";
import { MessageSquare, User, Bot, Send } from "lucide-react";
import { Card } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { VoiceButton } from "./VoiceButton";
import { WindAndLeavesLoading } from "./WindAndLeavesLoading";

export interface ConversationMessage {
  id: string;
  type: "user" | "assistant";
  message: string;
  timestamp: Date;
}

interface VoiceAssistantPanelProps {
  conversations: ConversationMessage[];
  onSendMessage?: (message: string) => void;
  onVoiceInput?: (userMessage: string, aiResponse: string) => void;
  isParsing?: boolean
}

export function VoiceAssistantPanel({ conversations, onSendMessage, onVoiceInput, isParsing }: VoiceAssistantPanelProps) {
  const [inputMessage, setInputMessage] = useState("");

  const handleSend = () => {
    if (inputMessage.trim() && onSendMessage) {
      onSendMessage(inputMessage);
      setInputMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  return (
    <div className="w-80 border-l bg-white flex flex-col">

      <ScrollArea className="flex-1 p-6">
        <div className="space-y-4">
          {conversations.length > 0 ? (
            conversations.map((conv) => (
              <div
                key={conv.id}
                className={`flex gap-3 ${
                  conv.type === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {conv.type === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-blue-600" />
                  </div>
                )}
                
                <Card
                  className={`p-3 max-w-[80%] ${
                    conv.type === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100"
                  }`}
                >
                  <p className="text-sm">{conv.message}</p>
                  <p
                    className={`text-xs mt-1 ${
                      conv.type === "user" ? "text-blue-100" : "text-gray-500"
                    }`}
                  >
                    {conv.timestamp.toLocaleTimeString("ko-KR", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </Card>

                {conv.type === "user" && (
                  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <div className="mb-4 flex justify-center">
                <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
                  <MessageSquare className="w-8 h-8 text-gray-400" />
                </div>
              </div>
              <h3 className="mb-2">대화 내역이 없습니다</h3>
              <p className="text-sm text-gray-500">
                아래 입력창이나 음성 버튼을 눌러 일정을 관리해보세요
              </p>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="border-t p-4">
        {isParsing ? (
          <div className="flex flex-col items-center justify-center gap-2 text-sm text-gray-500">
            <WindAndLeavesLoading />
            <span>AI가 응답을 생성중입니다...</span>
          </div>
        ) : (
          <div className="flex gap-2">
            <Input
              type="text"
              placeholder="메시지를 입력하세요..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyUp={handleKeyPress}
              className="flex-1"
              disabled={isParsing}
            />
            <Button onClick={handleSend} size="icon" disabled={isParsing}>
              <Send className="w-4 h-4" />
            </Button>
            {onVoiceInput && <VoiceButton onVoiceInput={onVoiceInput} disabled={isParsing} />}
          </div>
        )}
      </div>
    </div>
  );
}
