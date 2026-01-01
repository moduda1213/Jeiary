import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { parseTextWithAI } from '@/api/ai';
// import { createSchedule } from '@/api/schedule';
import { type ChatMessage } from '@/types';
import ChatInput from '@/components/ChatInput';
import useSpeechRecognition from '@/hooks/useSpeechRecognition';

const ChatDashboard: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    hasRecognitionSupport
   } = useSpeechRecognition();

  // 자동 스크롤
  useEffect(() => {
    if (transcript) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      setInputValue(prev => prev ? `${prev} ${transcript}` : transcript);
    }
    
  }, [transcript]);

  // useEffect(() => {
  //   // 1. 듣기가 끝났고(!isListening)
  //   // 2. 변환된 텍스트가 있고(transcript)
  //   // 3. 처리 중이 아닐 때(!isProcessing)
  //   if (!isListening && transcript && !isProcessing) {
  //     const timer = setTimeout(() => {
  //       handleSend();
  //     }, 800);

  //     return () => clearTimeout(timer);
  //   }
  // }, [isListening, transcript, isProcessing]);

  const handleSend = async () => {
    if (!inputValue.trim() || isProcessing) return;

    const userText = inputValue;
    setInputValue('');
    
    // 1. 사용자 메시지 추가
    const userMsg: ChatMessage = {
      id: Date.now(),
      role: 'user',
      text: userText,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setIsProcessing(true);

    try {
      // 2. AI API 호출
      const response = await parseTextWithAI(userText);
      let aiText = '';
      if (response.is_complete && response.data) {
          aiText = `일정이 등록되었습니다: "${response.data.title}" (${response.data.date})`;
      } else {
        aiText = response.question || "죄송합니다. 요청을 이해하지 못했습니다.";
      }
      // 4. AI 응답 추가
      const aiMsg: ChatMessage = {
        id: (Date.now() + 1),
        role: 'model',
        text: aiText,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMsg]);

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, {
        id: Date.now(),
        role: 'model',
        text: "시스템 오류가 발생했습니다.",
        timestamp: new Date()
      }]);

    } finally {
      setIsProcessing(false);
    }
  };

  // 1. 빈 상태 UI (publ 스타일)
  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center bg-white p-6 text-center dark:bg-[#101922]">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">안녕하세요, {user?.name || user?.email.split('@')[0]}님!</h1>
        <p className="mt-2 text-gray-500 dark:text-gray-400">무엇을 도와드릴까요? 아래에 입력하여 일정을 관리해보세요.</p>
        <div className="mt-8 grid w-full max-w-2xl grid-cols-1 gap-4 sm:grid-cols-2">
          <button 
            onClick={() => setInputValue("내일 오후 3시에 팀 회의 추가해줘")}
            className="flex flex-col items-start rounded-lg border border-gray-200 bg-gray-50 p-4 text-left transition-colors hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 
       dark:hover:bg-gray-700"
          >
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary">add_circle</span>
              <h3 className="text-sm font-medium text-gray-900 dark:text-white">일정 추가하기</h3>
            </div>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">"내일 오후 3시에 팀 회의 추가해줘" 와 같이 말해보세요.</p>
          </button>
          <button
            onClick={() => setInputValue("이번 주 내 일정 보여줘")}
            className="flex flex-col items-start rounded-lg border border-gray-200 bg-gray-50 p-4 text-left transition-colors hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800
       dark:hover:bg-gray-700"
          >
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary">search</span>
              <h3 className="text-sm font-medium text-gray-900 dark:text-white">일정 확인하기</h3>
            </div>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">"이번 주 내 일정 보여줘" 라고 물어보세요.</p>
          </button>
        </div>
        {/* 하단 입력창 (고정) */}
        <div className="fixed bottom-0 w-full max-w-[calc(100%-256px)] bg-white p-6 shadow-[0_-2px_4px_rgba(0,0,0,0.02)] dark:bg-[#101922]">
            <ChatInput 
                value={inputValue}
                onChange={setInputValue}
                onSend={handleSend}
                disabled={!inputValue.trim()} // 빈 상태에서는 isProcessing 체크 불필요
                isListening={isListening}
                startListening={startListening}
                stopListening={stopListening}
                hasRecognitionSupport={hasRecognitionSupport}
            />
        </div>
      </div>
    );
  }
  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto bg-white p-6 dark:bg-[#101922]">
        <div className="mx-auto flex max-w-3xl flex-col gap-6 pb-24">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex items-end gap-3 ${msg.role === 'user' ? 'justify-end ml-auto' : ''} max-w-[80%]`}>
                <div className={`flex flex-col gap-1 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                    <span className="text-xs text-gray-500">{msg.role === 'user' ? '나' : 'AI 비서'}</span>
                    {/* 4. 말풍선 스타일 */}
                    <div className={`rounded-2xl px-4 py-3 text-base leading-normal shadow-sm ${
                        msg.role === 'user'
                        ? 'bg-primary text-white rounded-br-none'
                        : 'bg-gray-100 text-gray-900 rounded-bl-none dark:bg-gray-800 dark:text-white'
                    }`}>
                        <p className="whitespace-pre-wrap">{msg.text}</p>
                    </div>
                </div>
            </div>
          ))}
          {/* 로딩 상태 (애니메이션) */}
          {isProcessing && (
             <div className="flex items-end gap-3 max-w-[80%]">
                <div className="flex flex-col gap-1 items-start">
                    <span className="text-xs text-gray-500">AI 비서</span>
                    <div className="bg-gray-100 text-gray-900 rounded-2xl rounded-bl-none px-4 py-3 dark:bg-gray-800 dark:text-white">
                        <div className="flex gap-1">
                            <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400"></div>
                            <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-75"></div>
                            <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-150"></div>
                        </div>
                    </div>
                </div>
             </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
      {/* 3. 하단 입력창 (채팅 모드) */}
      <div className="w-full border-t border-gray-200 bg-white px-6 py-4 shadow-[0_-2px_4px_rgba(0,0,0,0.02)] dark:border-gray-700 dark:bg-[#101922]">
        <ChatInput 
            value={inputValue}
            onChange={setInputValue}
            onSend={handleSend}
            disabled={!inputValue.trim()} // 빈 상태에서는 isProcessing 체크 불필요
            isListening={isListening}
            startListening={startListening}
            stopListening={stopListening}
            hasRecognitionSupport={hasRecognitionSupport}
        />
      </div>
    </div>
  );
};
export default ChatDashboard;