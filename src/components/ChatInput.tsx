"use client";

import { KeyboardEvent } from "react";
import { Send, Paperclip, X } from "lucide-react";

interface ChatInputProps {
  value: string;
  onChange: (v: string) => void;

  files: File[];
  onAddFiles: (files: File[]) => void;
  onRemoveFile: (i: number) => void;

  onSend: () => void;
  onPrepareDraft: () => void;
}

export default function ChatInput({
  value,
  onChange,
  files,
  onAddFiles,
  onRemoveFile,
  onSend,
  onPrepareDraft,
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
      {files.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {files.map((file, idx) => (
            <div
              key={`${file.name}-${idx}`}
              className="flex items-center gap-2 rounded-lg border border-gray-300 bg-gray-50 px-3 py-1 text-xs"
            >
              <span className="max-w-[160px] truncate text-black">
                {file.name}
              </span>
              <button
                onClick={() => onRemoveFile(idx)}
                className="text-gray-400 hover:text-gray-600"
                title="Remover arquivo"
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}

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

            if (files.length + selected.length > 20) {
              alert("O limite máximo é de 20 arquivos simultâneos.");
              return;
            }

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
          title="Preparar dados do contrato"
          className="
            h-11
            px-3
            rounded-xl
            border border-amber-300
            bg-amber-100
            text-amber-700
            text-sm
            font-medium
            hover:bg-amber-200
            transition
            whitespace-nowrap
          "
        >
          Preparar dados
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
