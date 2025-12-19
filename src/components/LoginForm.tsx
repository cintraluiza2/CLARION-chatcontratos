"use client";

import { useState } from "react";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = () => {
    if (!email || !password) {
      alert("Preencha email e senha");
      return;
    }

    alert(`Login com: ${email}`);
  };

  return (
    <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-amber-500 to-amber-600 px-8 py-12 text-center">
        <div className="w-20 h-20 bg-white rounded-full mx-auto mb-4 flex items-center justify-center shadow-lg">
          <span className="text-3xl font-bold text-amber-500">C</span>
        </div>

        <h1 className="text-3xl font-bold text-white">
          Bem-vindo de volta
        </h1>
        <p className="text-white/90 mt-2">
          Entre com suas credenciais
        </p>
      </div>

      {/* Form */}
      <div className="px-8 py-10 space-y-6">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-amber-500 focus:outline-none text-black placeholder:text-gray-400"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Senha
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:border-amber-500 focus:outline-none text-black placeholder:text-gray-400"
          />
        </div>

        <button
          onClick={handleSubmit}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 text-white font-bold text-lg hover:brightness-110 transition"
        >
          Entrar
        </button>
      </div>
    </div>
  );
}
