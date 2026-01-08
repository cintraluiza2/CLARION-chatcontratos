"use client";

import { KeyboardEvent } from "react";
import { Send, Paperclip, X } from "lucide-react";

interface ChatInputProps {
  value: string;
  onChange: (v: string) => void;

  onAddFiles: (files: File[]) => void;

  onSend: () => void;
  onPrepareDraft: () => void;
  hasDocuments: boolean;
}
export default function ChatInput({
  value,
  onChange,
  onAddFiles,
  onSend,
  onPrepareDraft,
  hasDocuments,
}: ChatInputProps) {
  /* =========================
     SEND
     ========================= */
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white px-6 py-4">
      {/* FILE LIST */}


      {/* INPUT ROW */}
      <div className="flex items-center gap-3">
        {/* Upload */}
        <input
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg,.docx,.xlsx"
          id="file-upload"
          className="hidden"
          onChange={(e) => {
            if (!e.target.files) return;

            const selected = Array.from(e.target.files);

            onAddFiles(selected);
            e.target.value = "";
          }}
        />

        <label
          htmlFor="file-upload"
          className="
            h-11 w-11
            flex items-center justify-center
            rounded-xl
            bg-amber-500
            hover:brightness-110
            cursor-pointer
            transition
          "
          title="Adicionar arquivos"
        >
          <Paperclip size={22} className="text-white" />
        </label>

        {/* Text input (reduced) */}
        <input
          type="text"
          placeholder="Digite sua mensagem…"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          className="
            flex-1
            h-11
            rounded-xl
            border border-gray-300
            px-4
            text-sm
            text-black
            placeholder-gray-400
            focus:outline-none
            focus:ring-2
            focus:ring-gray-300
          "
        />

        {/* Prepare draft */}
        <button
          onClick={onPrepareDraft}
          disabled={!hasDocuments}
          title="Consolidar Contrato"
          className={`
            h-11
            px-3
            rounded-xl
            text-sm
            font-medium
            transition
            whitespace-nowrap
            ${hasDocuments
              ? "border border-amber-300 bg-amber-100 text-amber-700 hover:bg-amber-200"
              : "border border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed"
            }
          `}
        >
          Consolidar Contrato
        </button>

        {/* Send */}
        <button
          onClick={onSend}
          title="Enviar"
          className="
            h-11 w-11
            flex items-center justify-center
            rounded-xl
            bg-amber-500
            hover:brightness-110
            transition
          "
        >
          <Send size={20} className="text-white" />
        </button>
      </div>
    </div>
  );
}
