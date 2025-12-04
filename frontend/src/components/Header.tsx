import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import logo from "../assets/Jeiary_logo_ver2.png";

interface HeaderProps {
  isLoggedIn: boolean;
  onLogout: () => void;
  onNavigateHome?: () => void;
}

export function Header({ isLoggedIn, onLogout, onNavigateHome }: HeaderProps) {
  return (
    <header className="h-16 border-b bg-white flex items-center justify-between px-6">
      <div>
        <button 
          onClick={onNavigateHome}
          className="flex items-center gap-2 hover:opacity-80 transition-opacity"
        >
          <ImageWithFallback 
            src={logo}
            alt="Jeiary Logo"
            className="h-8 w-auto"
          />
        </button>
      </div>
      
      <div>
        {isLoggedIn ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                <Avatar>
                  <AvatarImage src="" />
                  <AvatarFallback>사용자</AvatarFallback>
                </Avatar>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>마이페이지</DropdownMenuItem>
              <DropdownMenuItem>설정</DropdownMenuItem>
              <DropdownMenuItem onClick={onLogout}>로그아웃</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          // 로그인 상태가 아닐 때는 App.tsx에서 LoginPage를 렌더링하므로
          // Header 컴포넌트에서는 로그인 버튼이 필요 X
          null
        )}
      </div>
    </header>
  );
}
