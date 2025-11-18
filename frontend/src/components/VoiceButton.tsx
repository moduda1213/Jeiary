import { useState } from "react";
import { Mic } from "lucide-react";
import { motion } from "motion/react";

interface VoiceButtonProps {
  onVoiceInput: (userMessage: string, aiResponse: string) => void;
}

export function VoiceButton({ onVoiceInput }: VoiceButtonProps) {
  const [isActive, setIsActive] = useState(false);

  const handleClick = () => {
    if (!isActive) {
      setIsActive(true);
      
      // 음성 인식 시뮬레이션 (실제 구현 시 음성 API 연동)
      setTimeout(() => {
        const mockUserMessages = [
          "내일 오후 3시에 회의 일정 추가해줘",
          "다음 주 월요일 일정 알려줘",
          "오늘 일정 취소해줘",
          "이번 주 금요일에 점심 약속 추가",
        ];
        
        const mockAIResponses = [
          "정상적으로 일정을 추가했습니다.",
          "다음 주 월요일에 2개의 일정이 있습니다.",
          "오류가 발생해 진행하지 못했습니다. 다시 시도해주세요.",
          "금요일 12시에 점심 약속을 추가했습니다.",
        ];
        
        const randomIndex = Math.floor(Math.random() * mockUserMessages.length);
        const userMessage = mockUserMessages[randomIndex];
        const aiResponse = mockAIResponses[randomIndex];
        
        onVoiceInput(userMessage, aiResponse);
        setIsActive(false);
      }, 2000);
    }
  };

  return (
    <div className="relative">
      <motion.button
        onClick={handleClick}
        className={`relative w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
          isActive ? "bg-red-500" : "bg-blue-600"
        } text-white shadow-md hover:shadow-lg`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {isActive && (
          <>
            <motion.div
              className="absolute inset-0 rounded-full bg-red-400"
              initial={{ scale: 1, opacity: 0.6 }}
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.6, 0, 0.6],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
            <motion.div
              className="absolute inset-0 rounded-full bg-red-300"
              initial={{ scale: 1, opacity: 0.4 }}
              animate={{
                scale: [1, 1.8, 1],
                opacity: [0.4, 0, 0.4],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
                delay: 0.3,
              }}
            />
          </>
        )}
        <Mic className="w-5 h-5 relative z-10" />
      </motion.button>
      
      {isActive && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute bottom-12 right-0 bg-white px-3 py-1.5 rounded-lg shadow-lg whitespace-nowrap"
        >
          <p className="text-xs text-gray-700">음성 인식 중...</p>
        </motion.div>
      )}
    </div>
  );
}
