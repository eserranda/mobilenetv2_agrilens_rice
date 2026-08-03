"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Leaf,
  History as HistoryIcon,
  User,
  Plus,
  Menu,
  X,
  Compass,
  Settings
} from "lucide-react";
import "./globals.css";
import { cn } from "@/lib/utils";
import { getSetting, updateSetting } from "@/lib/api";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [openaiGuardrail, setOpenaiGuardrail] = useState<boolean>(true);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  // Fetch setting on load
  useEffect(() => {
    fetchGuardrailSetting();
  }, []);

  const fetchGuardrailSetting = async () => {
    try {
      const data = await getSetting("openai_guardrail");
      setOpenaiGuardrail(data.value === "true");
    } catch (err) {
      console.error("Failed to load setting:", err);
    }
  };

  const handleGuardrailToggle = async (value: boolean) => {
    setOpenaiGuardrail(value);
    try {
      await updateSetting("openai_guardrail", value ? "true" : "false");
    } catch (err) {
      console.error("Failed to save setting:", err);
    }
  };

  const menuItems = [
    { name: "Detection", href: "/detection?reset=true", icon: Leaf },
    { name: "History", href: "/history", icon: HistoryIcon },
    // { name: "Profile", href: "#", icon: User },
  ];

  const handleStartNewScan = () => {
    setIsMobileMenuOpen(false);
    // Navigate to root with reset param to trigger state clearing
    router.push("/detection");
  };

  const isLandingPage = pathname === "/";

  if (isLandingPage) {
    return (
      <html lang="en" className="h-full antialiased scroll-smooth">
        <body className="min-h-screen w-full bg-slate-50 text-slate-900 font-sans antialiased overflow-x-hidden selection:bg-emerald-500/20 selection:text-emerald-900">
          {children}
        </body>
      </html>
    );
  }

  return (
    <html lang="en" className="h-full antialiased">
      <body className="h-screen w-screen flex bg-slate-950 text-slate-100 font-sans overflow-hidden">

        {/* DESKTOP SIDEBAR */}
        <aside className="hidden md:flex w-72 bg-slate-950 border-r border-slate-905 flex-col shrink-0">
          {/* Header */}
          <div className="p-6 border-b border-slate-900">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Compass className="h-5 w-5" />
              </div>
              <div>
                <Link href="/" className="font-extrabold text-lg leading-none tracking-tight text-white">Agrilens Pro</Link>
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
              {/* Settings Dialog (Mobile) */}
              <Dialog open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
                <DialogTrigger render={
                  <button className="text-slate-400 hover:text-white transition p-1.5 hover:bg-slate-900 rounded-lg" title="Pengaturan">
                    <Settings className="h-5 w-5" />
                  </button>
                } />
                <DialogContent className="sm:max-w-md bg-slate-900 border border-slate-800 text-white rounded-3xl p-6">
                  <DialogHeader>
                    <DialogTitle className="text-lg font-bold text-slate-200">Pengaturan Analisis</DialogTitle>
                    <DialogDescription className="text-xs text-slate-400 mt-1">
                      Konfigurasi bagaimana model AgriLens Pro memproses dan memvalidasi gambar.
                    </DialogDescription>
                  </DialogHeader>

                  {/* Switch Toggle for OpenAI Verification */}
                  <div className="my-6">
                    <div className="flex items-center justify-between p-4 border rounded-2xl bg-slate-950/20 border-slate-800 hover:border-slate-800 transition duration-300">
                      <div className="flex flex-col pr-4">
                        <span className="text-xs font-bold text-slate-200">Verifikasi Gambar (OpenAI Vision Guardrail)</span>
                        <span className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                          Menyaring gambar yang bukan daun padi (seperti foto manusia, hewan, makanan) sebelum inferensi dijalankan untuk menghindari salah klasifikasi.
                        </span>
                      </div>

                      {/* Switch Toggle Button */}
                      <button
                        type="button"
                        role="switch"
                        aria-checked={openaiGuardrail}
                        onClick={() => handleGuardrailToggle(!openaiGuardrail)}
                        className={cn(
                          "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-emerald-500/25 focus:ring-offset-2 focus:ring-offset-slate-900",
                          openaiGuardrail ? "bg-emerald-600" : "bg-slate-800"
                        )}
                      >
                        <span
                          className={cn(
                            "pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out",
                            openaiGuardrail ? "translate-x-5" : "translate-x-0"
                          )}
                        />
                      </button>
                    </div>
                  </div>

                  <DialogFooter className="border-t border-slate-800/60 pt-4 flex gap-2">
                    <DialogClose render={
                      <Button variant="outline" className="w-full py-2.5 bg-slate-950/40 border-slate-800 hover:bg-slate-900 rounded-xl text-xs text-slate-400 font-bold hover:text-white transition">
                        Tutup
                      </Button>
                    } />
                  </DialogFooter>
                </DialogContent>
              </Dialog>

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
