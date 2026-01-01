import React, { useState, useEffect } from 'react';
import { User, ViewState, CalendarEvent, ChatMessage } from './types';
import { Sidebar } from './components/Sidebar';
import { Auth } from './components/Auth';
import { CalendarView } from './pages/CalendarView';
import { ChatDashboard } from './pages/ChatDashboard';

// Mock User Data
const MOCK_USER: User = {
  id: 'u1',
  name: '김민준',
  email: 'minjun.kim@example.com',
  avatarUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCH357ZvrwPubWqn1LEJvHM2j8XkEWTGsMUmfFd3RNdBxhZvKNmKiEBsT6jIHLoQ6YctOPLVzvGN7ILZV-lNhF2-nN0L2fjUdE7bS4pEgWLcCFHA5dYoWpIF6rwc4LJKfnUtSQqH8Mu2YDKrvH2u7KnOfs6UXFS-cpMS47AxAxA3mkX-qLvUJ6HS6JDzazoXK4TnrJ2QrhG4HvszfgtXKDvBsLfdDGIiKM9wSK8b-kB6V_fHu-4hCho_TJGDYdMzOcXVyBBulkdBA'
};

// Mock Events
const INITIAL_EVENTS: CalendarEvent[] = [
  {
    id: 'e1',
    title: '디자인 시안 제출',
    date: new Date(2024, 7, 5),
    startTime: '09:00',
    endTime: '10:00',
    colorClass: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
  },
  {
    id: 'e2',
    title: '팀 빌딩 활동',
    date: new Date(2024, 7, 6),
    startTime: '14:00',
    endTime: '16:00',
    colorClass: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
  },
  {
    id: 'e3',
    title: '프로젝트 회의',
    description: '3분기 프로젝트 진행 상황 공유 및 다음 단계 논의. 모든 팀원 참석 필수.',
    date: new Date(2024, 7, 12),
    startTime: '10:00',
    endTime: '11:30',
    colorClass: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
  }
];

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [currentView, setCurrentView] = useState<ViewState>(ViewState.LOGIN);
  const [events, setEvents] = useState<CalendarEvent[]>(INITIAL_EVENTS);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // Handle Login Simulation
  const handleLogin = () => {
    setUser(MOCK_USER);
    setCurrentView(ViewState.HOME);
  };

  // Handle Logout
  const handleLogout = () => {
    setUser(null);
    setCurrentView(ViewState.LOGIN);
    setMessages([]);
  };

  // Navigation Handler
  const handleNavigate = (view: ViewState) => {
    setCurrentView(view);
  };

  // Event Handlers
  const addEvent = (newEvent: CalendarEvent) => {
    setEvents([...events, newEvent]);
    setCurrentView(ViewState.CALENDAR);
  };

  const deleteEvent = (id: string) => {
    setEvents(events.filter(e => e.id !== id));
  };

  // Chat Handler
  const handleChatMessage = (text: string, isAiResponse: boolean = false) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      role: isAiResponse ? 'model' : 'user',
      text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);

    // Logic to switch to calendar if user asks (simple heuristic for demo)
    if (!isAiResponse && (text.includes('일정 보여줘') || text.includes('calendar'))) {
       setTimeout(() => setCurrentView(ViewState.CALENDAR), 1000);
    }
  };

  // If not logged in, show auth screens
  if (!user || currentView === ViewState.LOGIN || currentView === ViewState.SIGNUP || currentView === ViewState.FORGOT_PASSWORD) {
    return (
      <Auth 
        currentView={currentView === ViewState.HOME ? ViewState.LOGIN : currentView} 
        onNavigate={handleNavigate} 
        onLogin={handleLogin} 
      />
    );
  }

  // Main App Layout
  return (
    <div className="flex h-screen w-full overflow-hidden bg-white dark:bg-[#101922]">
      <Sidebar 
        user={user} 
        currentView={currentView} 
        onNavigate={handleNavigate} 
        onLogout={handleLogout} 
      />
      <main className="flex flex-1 flex-col overflow-hidden">
        {currentView === ViewState.CALENDAR ? (
          <CalendarView 
            events={events} 
            onAddEvent={addEvent} 
            onDeleteEvent={deleteEvent}
          />
        ) : (
          <ChatDashboard 
            user={user}
            messages={messages}
            onSendMessage={handleChatMessage}
          />
        )}
      </main>
    </div>
  );
}

export default App;
