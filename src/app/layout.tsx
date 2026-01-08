import "./globals.css";
import { Toaster } from "react-hot-toast";

export const metadata = {
  title: "Login",
  description: "Tela de login",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  );
}
