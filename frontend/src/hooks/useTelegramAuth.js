import { useEffect, useState, useCallback } from 'react';
import api from '@/api/api';

export function useTelegramAuth() {
  const [initData, setInitData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuth, setIsAuth] = useState(false);

  const handleAuth = useCallback(async () => {
    if (!initData) return;

    setLoading(true);

    try {
      const response = await api.post(`/auth/telegram/`, { init_data: initData });
      const access_token = response.data.access;

      if (access_token) {
        localStorage.setItem("access_token", access_token);
        setIsAuth(true);
      }
    } catch (error) {
      console.error("Telegram Auth Error:", error);
    } finally {
      setLoading(false);
    }
  }, [initData]);

  useEffect(() => {
    if (!window.Telegram?.WebApp) {
      setLoading(false);
      return;
    }

    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    if (tg.initData) {
      setInitData(tg.initData);
    } else {
      setLoading(false)
    }
  }, []);

  useEffect(() => {
    if (initData) {
      handleAuth();
    }
  }, [initData, handleAuth]);

  return { initData, loading, isAuth };
}
