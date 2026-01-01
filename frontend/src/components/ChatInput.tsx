import React from 'react';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
  
  // STT Props
  isListening: boolean;
  startListening: () => void;
  stopListening: () => void;
  hasRecognitionSupport: boolean;
  
  // 스타일 커스터마이징 (선택 사항)
  className?: string;
  placeholder?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  disabled,
  isListening,
  startListening,
  stopListening,
  hasRecognitionSupport,
  className = "",
  placeholder
}) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled) onSend();
    }
  };

  return (
    <div className={`relative mx-auto flex w-full max-w-3xl items-center ${className}`}>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        className="form-input flex h-14 w-full resize-none items-center rounded-xl border border-gray-300 bg-white py-4 pl-4 pr-24 text-base text-gray-900 shadow-sm placeholder:text-gray-500
                   focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400 overflow-hidden"
        placeholder={placeholder || (isListening ? "듣고 있어요... (말씀이 끝나면 멈춰주세요)" : "AI에게 메시지를 입력하거나 음성으로 요청하세요.")}
        rows={1}
      />
      <div className="absolute right-3 top-1/2 flex -translate-y-1/2 items-center gap-2">
        {/* 마이크 버튼 */}
        {hasRecognitionSupport && (
          <button
            type="button"
            onClick={isListening ? stopListening : startListening}
            className={`flex h-9 w-9 items-center justify-center rounded-full transition-colors ${
              isListening
                ? 'bg-red-100 text-red-600 hover:bg-red-200 animate-pulse'
                : 'text-primary hover:bg-primary/10'
            }`}
            title={isListening ? "녹음 중지" : "음성 입력"}
          >
            <span className="material-symbols-outlined text-[24px]">
              {isListening ? 'stop' : 'mic'}
            </span>
          </button>
        )}
        {/* 전송 버튼 */}
        <button
          onClick={onSend}
          disabled={disabled}
          className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white shadow-sm hover:bg-primary/90 transition-colors disabled:bg-gray-300 dark:disabled:bg-gray-700"
        >
          <span className="material-symbols-outlined text-[24px]">arrow_upward</span>
        </button>
      </div>
    </div>
  );
};
export default ChatInput;