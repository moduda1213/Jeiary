import { Calendar } from "lucide-react";

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-white h-full">
      <nav className="p-4">
        <ul className="space-y-2">
          <li>
            <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors">
              <Calendar className="w-5 h-5" />
              <span>일정</span>
            </button>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
