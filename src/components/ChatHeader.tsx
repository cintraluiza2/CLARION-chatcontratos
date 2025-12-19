"use client";

import { LogOut } from "lucide-react";

export default function ChatHeader({
  onLogout,
}: {
  onLogout: () => void;
}) {
  return (
    <header className="h-14 bg-white border-b flex items-center justify-end px-6">
      <button
        type="button"
        onClick={onLogout}
        className="text-gray-400 hover:text-gray-600 cursor-pointer transition"
        title="Sair"
      >
        <LogOut size={20} />
      </button>
    </header>
  );
}
