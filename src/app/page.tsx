"use client";

import { useEffect, useState, DragEvent } from "react";
import { useRouter } from "next/navigation";

import ChatSidebar from "../components/ChatSideBar";
import ChatHeader from "../components/ChatHeader";
import ChatMessage from "../components/ChatMessage";
import ChatInput from "../components/ChatInput";

/* =========================
   TYPES
   ========================= */
type Message = {
  id: number;
  role: "user" | "bot";
  content: string;
};

type PendingInstruction = {
  path: string;
  new_value: any;
  description: string;
};

/* =========================
   UTILS
   ========================= */
const setByPath = (obj: any, path: string, value: any) => {
  const parts: (string | number)[] = [];

  path.split(".").forEach((chunk) => {
    const re = /([^[\]]+)|\[(\d+)\]/g;
    let match: RegExpExecArray | null;
    while ((match = re.exec(chunk)) !== null) {
      if (match[1]) parts.push(match[1]);
      if (match[2]) parts.push(Number(match[2]));
    }
  });

  const clone = structuredClone(obj ?? {});
  let cur = clone;

  for (let i = 0; i < parts.length - 1; i++) {
    const key = parts[i];
    const next = parts[i + 1];

    if (typeof key === "number") {
      if (!Array.isArray(cur)) return clone;
      if (cur[key] == null) cur[key] = typeof next === "number" ? [] : {};
      cur = cur[key];
    } else {
      if (cur[key] == null) cur[key] = typeof next === "number" ? [] : {};
      cur = cur[key];
    }
  }

  const last = parts[parts.length - 1];
  if (typeof last === "number") {
    if (Array.isArray(cur)) cur[last] = value;
  } else {
    cur[last] = value;
  }

  return clone;
};

const unwrapResponseText = (payload: any): string => {
  if (payload == null) return "";
  if (typeof payload === "string") return payload;
  if (typeof payload.response === "string") return payload.response;
  if (payload.response && typeof payload.response === "object") {
    const inner = unwrapResponseText(payload.response);
    if (inner) return inner;
  }
  try {
    return JSON.stringify(payload, null, 2);
  } catch {
    return String(payload);
  }
};

/* =========================
   PAGE
   ========================= */
export default function ChatPage() {
  const router = useRouter();

  const [messages, setMessages] = useState<Message[]>([]);
  const [documents, setDocuments] = useState<Record<string, any>>({});
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [contractDraft, setContractDraft] = useState<any | null>(null);
  const [templateKey, setTemplateKey] = useState<"compra-venda" | "financiamento-go" | "financiamento-ms">("compra-venda");
  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";


  // ✅ Armazena instruções de edição ANTES do draft ser criado
  const [pendingInstructions, setPendingInstructions] = useState<PendingInstruction[]>([]);

  /* =========================
     AUTH GUARD
     ========================= */
  useEffect(() => {
    const email = localStorage.getItem("email");
    if (!email) router.replace("/");
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("email");
    router.push("/");
  };

  /* =========================
     FILES
     ========================= */
  const addFiles = (files: File[]) => {
    const allowedExtensions = [".pdf", ".png", ".jpg", ".jpeg", ".docx", ".xlsx"];
    const validFiles = files.filter(file => {
      const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
      return allowedExtensions.includes(ext);
    });

    if (validFiles.length < files.length) {
      alert("Ops! Só aceitamos documentos PDF, Imagens, Word ou Excel por enquanto.");
    }

    if (validFiles.length === 0) return;

    setPendingFiles((prev) => {
      const merged = [...prev, ...validFiles];
      if (merged.length > 20) {
        alert("O limite máximo é de 20 arquivos simultâneos.");
      }
      return merged.slice(0, 20);
    });
  };

  const removeFile = (index: number) => {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE_URL}/api/ocr`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: "Erro desconhecido" }));
        throw new Error(errorData.detail || "Erro ao processar documento");
      }

      const data = await res.json();
      const extracted = data.result ?? data.data ?? data;
      const fullText = data.text ?? data.result_text ?? data.result ?? "";

      setDocuments((prev) => ({
        ...prev,
        [file.name]: extracted,
      }));

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "bot",
          content: `📄 **${file.name}**\n\n${typeof fullText === "string" ? fullText : JSON.stringify(fullText, null, 2)}`,
        },
      ]);
    } catch (err: any) {
      console.error("OCR Error:", err);
      const errorMessage = err.message === "Failed to fetch"
        ? "Não foi possível conectar ao servidor. Verifique se o backend está rodando na porta 8000."
        : err.message;

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "bot",
          content: `❌ **Erro no arquivo ${file.name}:** ${errorMessage}`,
        },
      ]);
    }
  };

  /* =========================
     SEND MESSAGE
     ========================= */
  const handleSend = async () => {
    if (!inputValue.trim() && pendingFiles.length === 0) return;

    const userText = inputValue.trim();

    if (userText) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: "user", content: userText },
      ]);
      setInputValue("");
    }

    setLoading(true);

    // Upload files
    for (const file of pendingFiles) {
      await handleUpload(file);
    }
    setPendingFiles([]);

    // ✅ SE JÁ TEM DRAFT → Edita o draft existente
    if (userText && contractDraft) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/edit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            draft: contractDraft,
            message: userText,
          }),
        });

        if (!res.ok) {
          const errorData = await res.json().catch(() => ({ detail: "Erro ao editar" }));
          throw new Error(errorData.detail || "Erro ao editar");
        }

        const data = await res.json();

        if (data.instruction) {
          setContractDraft((prev: any) =>
            setByPath(prev, data.instruction.path, data.instruction.new_value)
          );

          setMessages((prev) => [
            ...prev,
            {
              id: Date.now() + 2,
              role: "bot",
              content: `✏️ **Alteração aplicada:**\n\`${data.instruction.path}\` → \`${JSON.stringify(data.instruction.new_value)}\`\n\n${data.instruction.description || ""}`,
            },
          ]);
        }
      } catch (err: any) {
        console.error("Edit Error:", err);
        const errorMessage = err.message === "Failed to fetch"
          ? "Não foi possível conectar ao servidor. Verifique se o backend está rodando na porta 8000."
          : err.message;

        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            role: "bot",
            content: `❌ **Opa!** ${errorMessage}`,
          },
        ]);
      }
    }
    // ✅ SE NÃO TEM DRAFT → Verifica se é instrução de edição
    else if (userText) {
      try {
        console.log("📤 Chamando /api/detect-edit com:", { message: userText });

        const editRes = await fetch(`${API_BASE_URL}/api/detect-edit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: userText,
            documents,
          }),
        });

        if (!editRes.ok) {
          const errorData = await editRes.json().catch(() => ({ detail: "Erro" }));
          throw new Error(errorData.detail || "Erro");
        }

        const editData = await editRes.json();

        console.log("📥 Resposta do detect-edit:", editData);

        if (editData.is_edit_instruction && editData.instruction) {
          // Armazena a instrução para aplicar depois
          setPendingInstructions((prev) => {
            const updated = [...prev, editData.instruction];
            console.log("💾 Instruções pendentes:", updated);
            return updated;
          });

          setMessages((prev) => [
            ...prev,
            {
              id: Date.now() + 1,
              role: "bot",
              content: `✅ **Entendido!** Quando gerar o contrato, vou aplicar:\n\n**${editData.instruction.description}**\n\`${editData.instruction.path}\` = \`${JSON.stringify(editData.instruction.new_value)}\``,
            },
          ]);
        } else {
          // Chat normal
          const chatRes = await fetch(`${API_BASE_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              history: messages.map((m) => ({
                role: m.role,
                content: m.content,
              })),
              documents,
              message: userText,
            }),
          });

          if (!chatRes.ok) {
            const errorData = await chatRes.json().catch(() => ({ detail: "Erro no chat" }));
            throw new Error(errorData.detail || "Erro no chat");
          }

          const chatData = await chatRes.json();
          const botText = unwrapResponseText(chatData);

          setMessages((prev) => [
            ...prev,
            {
              id: Date.now() + 1,
              role: "bot",
              content: botText,
            },
          ]);
        }
      } catch (err: any) {
        console.error("Chat Error:", err);
        const errorMessage = err.message === "Failed to fetch"
          ? "Não foi possível conectar ao servidor. Verifique se o backend está rodando na porta 8000."
          : err.message;

        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            role: "bot",
            content: `❌ **Opa!** ${errorMessage}`,
          },
        ]);
      }
    }

    setLoading(false);
  };

  /* =========================
     PREPARAR DRAFT
     ========================= */
  const prepareContractDraft = async () => {
    setLoading(true);

    console.log("📤 Enviando para /api/draft:", {
      documents: Object.keys(documents),
      pending_instructions: pendingInstructions
    });

    try {
      const res = await fetch(`${API_BASE_URL}/api/draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          documents,
          pending_instructions: pendingInstructions,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: "Erro ao preparar dados" }));
        throw new Error(errorData.detail || "Erro ao preparar dados");
      }

      const data = await res.json();

      console.log("📥 Draft recebido:", data);

      setContractDraft(data);

    } catch (err: any) {
      console.error("Draft Error:", err);
      const errorMessage = err.message === "Failed to fetch"
        ? "Não foi possível conectar ao servidor. Verifique se o backend está rodando na porta 8000."
        : err.message;
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /* =========================
     GERAR CONTRATO
     ========================= */
  const generateContract = async () => {
    if (!contractDraft) {
      alert("Prepare os dados do contrato primeiro.");
      return;
    }

    const res = await fetch(`${API_BASE_URL}/api/contract/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        template: templateKey,
        draft: contractDraft,
        extra_text: "",
      }),
    });

    if (!res.ok) {
      const err = await res.text().catch(() => "Erro ao gerar contrato");
      alert(err);
      return;
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `contrato_${templateKey}.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();

    window.URL.revokeObjectURL(url);
  };

  /* =========================
     DRAG & DROP
     ========================= */
  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(true);
  };

  const onDragLeave = () => setDragging(false);

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);

    if (e.dataTransfer.files.length > 0) {
      addFiles(Array.from(e.dataTransfer.files));
      e.dataTransfer.clearData();
    }
  };

  /* =========================
     RENDER
     ========================= */
  return (
    <div
      className="flex h-dvh bg-white relative"
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      {dragging && (
        <div className="absolute inset-0 z-50 bg-black/40 flex items-center justify-center pointer-events-none">
          <div className="rounded-xl bg-white px-6 py-4 text-sm font-medium shadow-lg">
            Solte os arquivos para enviar 📄
          </div>
        </div>
      )}

      <ChatSidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      <div className="flex flex-col flex-1">
        <ChatHeader onLogout={handleLogout} />

        <main className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {loading && (
            <ChatMessage
              message={{
                role: "bot",
                content: "Digitando...",
              }}
            />
          )}
        </main>

        {contractDraft && (
          <div className="border-t border-gray-200 bg-amber-50 px-6 py-4 text-black">
            <h2 className="text-lg font-semibold mb-3 text-black">
              📄 Dados consolidados do contrato
            </h2>

            {contractDraft.pendencias && contractDraft.pendencias.length > 0 && (
              <div className="mb-4 rounded-lg bg-red-100 border border-red-300 p-4">
                <h3 className="text-sm font-bold text-red-700 mb-2">⚠️ Pendências Identificadas:</h3>
                <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
                  {contractDraft.pendencias.map((p: string, i: number) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            )}

            <pre className="bg-white border border-gray-300 rounded-lg p-4 text-sm text-black overflow-auto max-h-[300px] whitespace-pre-wrap">
              {JSON.stringify(contractDraft, null, 2)}
            </pre>

            <div className="mt-4 flex items-center gap-3">
              <label className="text-sm text-black font-medium">Modelo:</label>

              <select
                value={templateKey}
                onChange={(e) => setTemplateKey(e.target.value as any)}
                className="h-10 rounded-lg border border-gray-300 bg-white px-3 text-sm text-black"
              >
                <option value="compra-venda">À vista</option>
                <option value="financiamento-go">Financiamento Goiânia</option>
                <option value="financiamento-ms">Financiamento Aparecida</option>
              </select>

              <button
                onClick={generateContract}
                className="h-10 px-4 rounded-lg bg-amber-500 text-black font-medium hover:brightness-110"
              >
                Gerar contrato (.docx)
              </button>
            </div>

            <div className="mt-4 flex gap-3">
              <button
                onClick={() => setContractDraft(null)}
                className="px-4 py-2 rounded-lg border border-gray-300 text-black hover:bg-gray-100"
              >
                Voltar ao chat
              </button>
            </div>
          </div>
        )}

        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          files={pendingFiles}
          onAddFiles={addFiles}
          onRemoveFile={removeFile}
          onSend={handleSend}
          onPrepareDraft={prepareContractDraft}
        />
      </div>
    </div>
  );
}
