"use client";

import {
  User,
  FileText,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import { useEffect, useState } from "react";

interface Props {
  open: boolean;
  onToggle: () => void;
}

export default function ChatSidebar({ open, onToggle }: Props) {
  const [nickname, setNickname] = useState("");

  useEffect(() => {
    const email = localStorage.getItem("email");
    if (email) setNickname(email.split("@")[0]);
  }, []);

  /* =========================
     COLLAPSED
     ========================= */
  if (!open) {
    return (
      <aside className="flex w-16 flex-col items-center bg-[#121212] border-r border-white/10 py-4">
        <button
          onClick={onToggle}
          className="text-gray-400 hover:text-white transition cursor-pointer"
        >
          <PanelLeftOpen size={20} />
        </button>
      </aside>
    );
  }

  /* =========================
     EXPANDED
     ========================= */
  return (
    <aside className="flex w-64 flex-col bg-[#121212] border-r border-white/10">
      {/* Header / Logo */}
      <div className="relative pl-2 pt-4 pb-2">
        <img
          src="/logo_clarion.png"
          alt="Clarion Logo"
          className="h-40 w-auto object-contain max-w-[85%]"
        />

        <button
          onClick={onToggle}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition cursor-pointer"
        >
          <PanelLeftClose size={18} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-2">
        <ul className="space-y-2">
          <li>
            <button
              className="
                flex w-full items-center gap-3
                rounded-xl px-4 py-3
                text-sm font-medium
                bg-amber-500/10 text-amber-400
                hover:bg-amber-500/20
                transition
                cursor-pointer
              "
            >
              <FileText size={18} />
              Gerar Contrato
            </button>
          </li>
        </ul>
      </nav>

      {/* Footer */}
      <div className="border-t border-white/10 px-6 py-4">
        {/* User */}
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-amber-500 flex items-center justify-center">
            <User size={18} className="text-black" />
          </div>

          <div className="flex flex-col leading-tight">
            <span className="text-sm font-medium text-white">
              Batista Advogados
            </span>
            <span className="text-xs text-gray-400">
              Conta ativa
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
