import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { parseTextWithAI } from '@/api/ai';
import { createSchedule } from '@/api/schedule';
import { type ChatMessage } from '@/types';

const ChatDashboard: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

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
        // 3. 일정 생성 자동 수행 (또는 사용자 확인 절차 추가 가능)
        try {
            await createSchedule({
                title: response.data.title,
                date: response.data.date,
                start_time: response.data.start_time,
                end_time: response.data.end_time,
                content: response.data.content
            });
            aiText = `일정이 등록되었습니다: "${response.data.title}" (${response.data.date})`;
        } catch (err) {
            aiText = "일정 정보를 파싱했지만, 등록 중 오류가 발생했습니다.";
        }
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
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
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
            <div className="relative mx-auto flex w-full max-w-3xl items-center">
                <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    className="form-input flex h-14 w-full resize-none items-center rounded-xl border border-gray-300 bg-white py-4 pl-4 pr-24 text-base text-gray-900 shadow-sm placeholder:text-gray-50
       focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400"
                    placeholder="AI에게 메시지를 입력하거나 음성으로 요청하세요."
                    rows={1}
                />
                <div className="absolute right-3 top-1/2 flex -translate-y-1/2 items-center gap-2">
                    <button className="flex h-9 w-9 items-center justify-center rounded-full text-primary hover:bg-primary/10 transition-colors">
                        <span className="material-symbols-outlined text-[24px]">mic</span>
                    </button>
                    <button
                        onClick={handleSend}
                        disabled={!inputValue.trim()}
                        className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white shadow-sm hover:bg-primary/90 transition-colors disabled:bg-gray-300
       dark:disabled:bg-gray-700"
                    >
                        <span className="material-symbols-outlined text-[24px]">arrow_upward</span>
                    </button>
                </div>
            </div>
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
                {/* 2. AI 아바타 (이미지 적용) */}
                {/* {msg.role === 'model' && (
                    <div
                        className="h-10 w-10 shrink-0 rounded-full bg-cover bg-center"
                        style={{ backgroundImage:
       'url("https://lh3.googleusercontent.com/aida-public/AB6AXuBryNAwNMNKlNmlimuTPyvgelwKp75psj7qstrJR40HVVBnMU1nS2ZtCS-kmeJFhRWKeS7SVL2NsIi0ec8Hp0Wp-VhsjJ_2XGHIuWgOvMZb5YRFFtKXASqMBnNIHiG17q5ZHkhmTHa04o8MFe7Z2-8I-P-fHyZmBV_OGLPQr3qH3f17EYxVXcYNa9INTM_OlLXH1daKBl5_NqXRkV_NIHqJVEo_ksgzvFWhBcwDRLelUJ1xpXlG_lQHN2YBPLahQ0kTVaZAZBVQ")' }}
                    ></div>
                )} */}
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
                {/* 2. 사용자 아바타 */}
                {/* {msg.role === 'user' && (
                    <div
                        className="h-10 w-10 shrink-0 rounded-full bg-cover bg-center bg-gray-200"
                        style={user?.avatarUrl ? { backgroundImage: `url("${user.avatarUrl}")` } : {}}
                    >
                         {!user?.avatarUrl && <span className="flex h-full w-full items-center justify-center text-xs text-gray-500">ME</span>}
                    </div>
                )} */}
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
        <div className="relative mx-auto flex w-full max-w-3xl items-center">
            <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                className="form-input flex h-14 w-full resize-none items-center rounded-xl border border-gray-300 bg-white py-4 pl-4 pr-24 text-base text-gray-900 shadow-sm placeholder:text-gray-500   
       focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400"
                placeholder="AI에게 메시지를 입력하거나 음성으로 요청하세요."
                rows={1}
            />
            <div className="absolute right-3 top-1/2 flex -translate-y-1/2 items-center gap-2">
                <button className="flex h-9 w-9 items-center justify-center rounded-full text-primary hover:bg-primary/10 transition-colors">
                    <span className="material-symbols-outlined text-[24px]">mic</span>
                </button>
                <button
                    onClick={handleSend}
                    disabled={!inputValue.trim() || isProcessing}
                    className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white shadow-sm hover:bg-primary/90 transition-colors disabled:bg-gray-300 dark:disabled:bg-gray-700" 
                >
                    <span className="material-symbols-outlined text-[24px]">arrow_upward</span>
                </button>
            </div>
        </div>
      </div>
    </div>
  );
};
export default ChatDashboard;