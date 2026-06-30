import { useEffect, useState } from "react";

/**
 * Интеграция с Telegram Mini App — [FE-08].
 * Когда приложение открыто внутри Telegram, инициализирует WebApp
 * (ready/expand), считывает тему и данные пользователя. Вне Telegram —
 * безопасно деградирует (isTelegram = false).
 */

interface TelegramWebApp {
  ready: () => void;
  expand: () => void;
  colorScheme?: "light" | "dark";
  themeParams?: { bg_color?: string };
  initDataUnsafe?: { user?: { id: number; first_name?: string; last_name?: string; username?: string } };
  setHeaderColor?: (color: string) => void;
}

declare global {
  interface Window {
    Telegram?: { WebApp?: TelegramWebApp };
  }
}

export interface TelegramState {
  isTelegram: boolean;
  webApp: TelegramWebApp | null;
}

export function useTelegram(): TelegramState {
  const [state, setState] = useState<TelegramState>({ isTelegram: false, webApp: null });

  useEffect(() => {
    const webApp = window.Telegram?.WebApp ?? null;
    if (!webApp) return;
    try {
      webApp.ready();
      webApp.expand();
      webApp.setHeaderColor?.("#4F46E5");
    } catch {
      /* в окружениях без полного API — игнорируем */
    }
    setState({ isTelegram: true, webApp });
  }, []);

  return state;
}
