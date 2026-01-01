import { useState, useEffect, useCallback } from "react";

// 타입 정의
// 방금 인식한 음성 데이터
interface SpeechRecognitionEvent {
    results: {
        [key: number]: { // 문장 인덱스
            [key: number]: { // 인식 후보 인덱스
                transcript: string;
            }
        }
    }
}

interface SpeechRecognitionErrorEvent {
    error: string;
}

interface SpeechRecognition extends EventTarget {
    continuous: boolean;
    interimResults: boolean;
    lang: string;
    start: () => void;
    stop: () => void;
    abort: () => void;
    onstart: () => void;
    onend: () => void;
    onresult: (evnet: SpeechRecognitionEvent) => void;
    onerror: (event: SpeechRecognitionErrorEvent) => void;
}

// Window 객체 확장
declare global {
    interface Window {
        webkitSpeechRecognition : any;
        SpeechRecognition: any;
    }
}

const useSpeechRecognition = () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState("");
    // 에러 상태 추가
    const [error, setError] = useState<string | null>(null);
    const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);

    useEffect(() => {
        // 브라우저 호환성 체크
        const SpeechRecognitionApi = window.webkitSpeechRecognition || window.SpeechRecognition;

        if (!SpeechRecognitionApi) {
            setError("이 브라우저는 음성 인식을 지원하지 않습니다.");
            return;
        }

        const recog = new SpeechRecognitionApi();
        recog.continuous = false; // true면 계속 듣기, false면 한 문장 후 종료
        recog.interimResults = true; // 실시간으로 변환되는 중간 결과 받기 (UX 향상)
        recog.lang = 'ko-KR';

        recog.onstart = () => {
            setIsListening(true);
            setError(null);
        };

        recog.onend = () => {
            setIsListening(false);
        };

        recog.onresult = (event: SpeechRecognitionEvent) => {
            // interimResults가 true일 때, 마지막 결과만 가져오기
            const lastResultIndex = Object.keys(event.results).length - 1;
            const text = event.results[lastResultIndex][0].transcript;
            setTranscript(text);
        };

        recog.onerror = (event: SpeechRecognitionErrorEvent) => {
            console.error("Speech recognition error:", event.error);
            setError(event.error); // 'not-allowed', 'no-speech' 등
            setIsListening(false);
        };

        setRecognition(recog);
    }, []);

    const startListening = useCallback(() => {
        if (recognition) {
            try {
                // 이전 결과 초기화
                setTranscript('');
                recognition.start();
            } catch (err) {
                // 이미 시작된 경우 등 예외 처리
                console.error(err);
            }
        }
    }, [recognition]);

    const stopListening = useCallback(() => {
        if (recognition) {
            recognition.stop();
        }
    }, [recognition]);

    return {
        isListening,
        transcript,
        error,
        startListening,
        stopListening,
        hasRecognitionSupport: !!recognition
    };
};

export default useSpeechRecognition;