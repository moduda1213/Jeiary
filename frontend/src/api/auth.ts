// src/api/auth.ts
import apiClient from './client';
import { type User } from '@/types';

/**
 * 로그인 API 호출
 * 백엔드의 OAuth2PasswordRequestForm은 'username' 필드에 이메일을 받습니다.
 * Content-Type: application/x-www-form-urlencoded
 */
export const login = async (email: string, password: string): Promise<void> => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    // 응답으로 Access Token이 쿠키에 설정됩니다 (HttpOnly).
    await apiClient.post('/auth/login', formData);
};

/**
 * 회원가입 API 호출
 * Content-Type: application/json
 */
export const signup = async (email: string, password: string): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', {
        email,
        password
    });
    return response.data;
};

/**
 * 로그아웃 API 호출
 */
export const logout = async (): Promise<void> => {
    await apiClient.post('/auth/logout');
};

/**
 * 현재 사용자 정보 조회 (세션 유지 확인)
 */
export const getMe = async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
};