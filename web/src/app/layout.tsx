import type { Metadata } from "next";
import { Poppins, Inter } from "next/font/google";
import { AuthProvider } from "@/contexts/AuthContext";
import "./globals.css";

const poppins = Poppins({
  variable: "--font-heading",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Chris AI - AI 数字员工平台",
  description: "企业内部的 AI 角色工作台 + 决策前哨站",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={`${poppins.variable} ${inter.variable}`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
