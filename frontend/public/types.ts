export enum ViewState {
  LOGIN = 'LOGIN',
  SIGNUP = 'SIGNUP',
  FORGOT_PASSWORD = 'FORGOT_PASSWORD',
  HOME = 'HOME', // This is the Chat/Dashboard
  CALENDAR = 'CALENDAR'
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl: string;
}

export interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  date: Date; // normalized to start of day for grouping
  startTime: string; // e.g. "10:00"
  endTime: string;   // e.g. "11:30"
  colorClass: string; // e.g. "bg-green-100 text-green-800"
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: Date;
  isTyping?: boolean;
}

export interface AuthContextType {
  user: User | null;
  login: () => void;
  logout: () => void;
}
