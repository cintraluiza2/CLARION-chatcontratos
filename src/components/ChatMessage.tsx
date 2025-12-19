import { User, Bot } from "lucide-react";

export default function ChatMessage({
  message,
}: {
  message: { role: "user" | "bot"; content: string };
}) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-4 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="w-9 h-9 rounded-full bg-gray-300 flex items-center justify-center">
          <Bot size={18} className="text-gray-700" />
        </div>
      )}

      <div
        className={`max-w-[70%] px-4 py-3 rounded-2xl text-sm text-black
          ${isUser ? "bg-amber-500" : "bg-gray-200"}`}
      >
        {message.content}
      </div>

      {isUser && (
        <div className="w-9 h-9 rounded-full bg-amber-500 flex items-center justify-center">
          <User size={18} className="text-black" />
        </div>
      )}
    </div>
  );
}
