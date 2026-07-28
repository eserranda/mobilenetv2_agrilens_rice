"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Geist, Geist_Mono } from "next/font/google";
import { 
  Leaf, 
  History as HistoryIcon, 
  User, 
  Plus, 
  Menu, 
  X,
  Compass
} from "lucide-react";
import "./globals.css";
import { cn } from "@/lib/utils";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const menuItems = [
    { name: "Detection", href: "/?reset=true", icon: Leaf },
    { name: "History", href: "/history", icon: HistoryIcon },
    { name: "Profile", href: "#", icon: User },
  ];

  const handleStartNewScan = () => {
    setIsMobileMenuOpen(false);
    // Navigate to root with reset param to trigger state clearing
    router.push("/?reset=true");
  };

  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="h-screen w-screen flex bg-slate-950 text-slate-100 font-sans overflow-hidden">
        
        {/* ============================================== DESKTOP SIDEBAR */}
        <aside className="hidden md:flex w-72 bg-slate-950 border-r border-slate-905 flex-col shrink-0">
          {/* Header */}
          <div className="p-6 border-b border-slate-900">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Compass className="h-5 w-5" />
              </div>
              <div>
                <h1 className="font-extrabold text-lg leading-none tracking-tight text-white">AgriLens Pro</h1>
                <p className="text-[10px] text-emerald-500 font-semibold tracking-wider uppercase mt-1">Precision Diagnostics</p>
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <nav className="flex-1 p-4 space-y-1.5">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href.split("?")[0];
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition duration-200 border border-transparent",
                    isActive 
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-sm shadow-emerald-500/5" 
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/50"
                  )}
                >
                  <Icon className={cn("h-5 w-5", isActive ? "text-emerald-400" : "text-slate-400")} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Start New Scan Button */}
          <div className="p-4 border-t border-slate-900">
            <button
              onClick={handleStartNewScan}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 rounded-xl font-bold flex items-center justify-center gap-2 transition duration-200 text-sm text-white shadow-lg shadow-emerald-600/15"
            >
              <Plus className="h-4.5 w-4.5" />
              Start New Scan
            </button>
          </div>
        </aside>

        {/* ============================================== MOBILE HEADER & MOBILE SIDEBAR DRAWER */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
          {/* Mobile top bar */}
          <header className="h-16 md:hidden bg-slate-950 border-b border-slate-900 px-4 flex items-center justify-between shrink-0 z-40">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsMobileMenuOpen(true)}
                className="p-2 -ml-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-900"
              >
                <Menu className="h-6 w-6" />
              </button>
              <h1 className="font-extrabold text-base text-white tracking-tight">AgriLens Pro</h1>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 overflow-hidden flex items-center justify-center">
                <User className="h-4.5 w-4.5 text-slate-400" />
              </div>
            </div>
          </header>

          {/* Mobile Drawer Overlay */}
          {isMobileMenuOpen && (
            <div 
              className="fixed inset-0 z-50 flex md:hidden bg-black/60 backdrop-blur-sm transition-opacity duration-300"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <div 
                className="w-72 h-full bg-slate-950 border-r border-slate-900 flex flex-col animate-in slide-in-from-left duration-300"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Header */}
                <div className="p-6 border-b border-slate-900 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Compass className="h-5 w-5 text-emerald-400" />
                    <h1 className="font-extrabold text-base text-white">AgriLens Pro</h1>
                  </div>
                  <button 
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="p-1 hover:bg-slate-905 rounded-lg text-slate-400"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                {/* Menu */}
                <nav className="flex-1 p-4 space-y-1.5">
                  {menuItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href.split("?")[0];
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className={cn(
                          "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition duration-200 border border-transparent",
                          isActive 
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
                            : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/50"
                        )}
                      >
                        <Icon className="h-5 w-5" />
                        {item.name}
                      </Link>
                    );
                  })}
                </nav>

                {/* Scan Button */}
                <div className="p-4 border-t border-slate-900">
                  <button
                    onClick={handleStartNewScan}
                    className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 rounded-xl font-bold flex items-center justify-center gap-2 transition duration-200 text-sm text-white"
                  >
                    <Plus className="h-4.5 w-4.5" />
                    Start New Scan
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Children container */}
          <main className="flex-1 flex flex-col overflow-hidden relative bg-slate-900 h-full min-h-0">
            {children}
          </main>
        </div>

      </body>
    </html>
  );
}
