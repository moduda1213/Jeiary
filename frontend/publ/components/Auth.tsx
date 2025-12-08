import React, { useState } from 'react';
import { ViewState } from '@/types';

interface AuthProps {
  currentView: ViewState;
  onNavigate: (view: ViewState) => void;
  onLogin: () => void;
}

export const Auth: React.FC<AuthProps> = ({ currentView, onNavigate, onLogin }) => {
  // Generic Input Component for reuse
  const InputField = ({ label, type, placeholder, id, icon = false }: any) => (
    <div className="flex flex-col">
      <label htmlFor={id} className="mb-2 text-base font-medium text-[#1E1E1E] dark:text-gray-300">
        {label}
      </label>
      <div className="relative flex w-full items-stretch">
        <input
          id={id}
          type={type}
          placeholder={placeholder}
          className="form-input h-12 w-full flex-1 rounded-lg border border-[#E0E0E0] bg-white p-3 text-base text-[#1E1E1E] placeholder:text-[#6B7280] focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400 dark:focus:border-primary"
        />
        {icon && (
          <button type="button" className="absolute inset-y-0 right-0 flex items-center pr-3 text-[#6B7280] hover:text-[#1E1E1E] dark:text-gray-400 dark:hover:text-white">
            <span className="material-symbols-outlined">visibility</span>
          </button>
        )}
      </div>
    </div>
  );

  const Button = ({ text, onClick }: { text: string; onClick?: () => void }) => (
    <button
      onClick={onClick}
      className="flex h-12 w-full cursor-pointer items-center justify-center rounded-lg bg-primary px-5 text-base font-bold text-white transition-colors hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
    >
      {text}
    </button>
  );

  if (currentView === ViewState.LOGIN) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-white p-6 dark:bg-background-dark">
        <div className="flex w-full max-w-2xl flex-col items-center gap-8 text-center">
            {/* Illustration Placeholder */}
          <div 
            className="aspect-video w-full max-w-[360px] bg-contain bg-center bg-no-repeat"
            style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuCPaRIKHLPm4xyboHn4jYx3GP3hP-QtFsz8YTLXYGhrXtQ2E2ibpupDSmGRXcDFtmwiJdSygVtX4TzrGtspimuhe6C_dTI-g7ecn8iuWjSYgHmEIwKgtO2aZQzekfYHCoUMRzQs5dM23nYg-S8ocLyzZBTOZR3tCmQfR1aK1plKTo2xxFN2FwzU9KqA4fd36p99Zkl9wM9Pwfd4XzcSX3lF9uT48HFWfLDdiJtvNGZG4RCXPgxKs8LOdClAR6-l46nCEwyKhSaVcQ')" }}
          ></div>
          
          <div className="flex max-w-[480px] flex-col items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
              로그인하여 일정을 관리하세요
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              앱의 핵심 기능을 활용하여 당신의 하루를 체계적으로 계획하고 관리할 수 있습니다.
            </p>
          </div>

          {/* Simple Login Form Container */}
          <div className="w-full max-w-sm space-y-4 text-left">
             <InputField id="login-email" label="이메일 주소" type="email" placeholder="example@email.com" />
             <InputField id="login-password" label="비밀번호" type="password" placeholder="********" icon={true} />
             
             <Button text="로그인 시작하기" onClick={onLogin} />
             
             <div className="flex justify-center gap-4 text-sm text-gray-500">
                <button onClick={() => onNavigate(ViewState.SIGNUP)} className="hover:text-primary">회원가입</button>
                <span>|</span>
                <button onClick={() => onNavigate(ViewState.FORGOT_PASSWORD)} className="hover:text-primary">비밀번호 찾기</button>
             </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentView === ViewState.SIGNUP) {
    return (
      <div className="relative flex min-h-screen w-full flex-col items-center justify-center bg-background-light p-4 dark:bg-background-dark">
        <div className="absolute inset-0 bg-slate-900/30 backdrop-blur-sm dark:bg-background-dark/60"></div>
        <div className="relative w-full max-w-md rounded-xl bg-white p-8 shadow-2xl dark:bg-[#101922] md:p-10">
          <h1 className="text-center text-3xl font-bold tracking-tight text-[#1E1E1E] dark:text-white">회원가입</h1>
          <div className="mt-8 flex flex-col gap-6">
            <InputField id="signup-email" label="이메일 주소" type="email" placeholder="example@email.com" />
            <InputField id="signup-password" label="비밀번호" type="password" placeholder="8자 이상 입력해주세요" icon={true} />
            <InputField id="signup-confirm" label="비밀번호 확인" type="password" placeholder="비밀번호를 다시 입력해주세요" icon={true} />
          </div>
          <div className="mt-8">
            <Button text="회원가입" onClick={() => onNavigate(ViewState.LOGIN)} />
          </div>
          <div className="mt-6 text-center">
            <p className="text-sm text-[#6B7280] dark:text-gray-400">
              이미 계정이 있으신가요?{' '}
              <button onClick={() => onNavigate(ViewState.LOGIN)} className="font-bold text-primary hover:underline">
                로그인
              </button>
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (currentView === ViewState.FORGOT_PASSWORD) {
    return (
      <div className="relative flex min-h-screen w-full flex-col items-center justify-center bg-background-light p-4 dark:bg-background-dark">
        <div className="absolute inset-0 bg-gray-900/50 dark:bg-black/60"></div>
        <div className="relative flex w-full max-w-md flex-col overflow-hidden rounded-xl bg-white shadow-2xl dark:bg-gray-800">
          <div className="absolute right-3 top-3">
            <button onClick={() => onNavigate(ViewState.LOGIN)} className="flex h-8 w-8 items-center justify-center rounded-full text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700">
              <span className="material-symbols-outlined text-2xl">close</span>
            </button>
          </div>
          <div className="flex flex-col items-center p-8 sm:p-10">
            <h3 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">비밀번호 찾기</h3>
            <p className="mt-2 text-center text-base font-normal text-gray-600 dark:text-gray-300">
              가입 시 사용한 이메일 주소를 입력하시면<br />
              비밀번호 재설정 링크를 보내드립니다.
            </p>
            <div className="mt-6 w-full">
              <InputField id="forgot-email" label="이메일 주소" type="email" placeholder="이메일 주소를 입력하세요" />
            </div>
            <div className="mt-6 w-full">
              <Button text="재설정 링크 보내기" onClick={() => alert("링크가 전송되었습니다.")} />
            </div>
            <button onClick={() => onNavigate(ViewState.LOGIN)} className="mt-8 text-center text-sm font-normal text-gray-500 underline hover:text-primary dark:text-gray-400">
              로그인으로 돌아가기
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};
