import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTelegramAuth } from '@/hooks/useTelegramAuth';
import { useMe } from '@/hooks/useMe';
import { AuthLoader } from '@/components/Loaders';
import NotInTelegram from '@/pages/NotInTelegram';
import TelegramAuthError from '@/pages/TelegramAuthError';
import api from '@/api/api';

export default function TelegramAuth({ children }) {
  const { initData, loading: telegramLoading, isAuth } = useTelegramAuth();
  const { user, loading: userLoading, error, refetch: userFetch } = useMe();
  const [isNavigate, setIsNavigate] = useState(false)
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (isAuth && !telegramLoading) {
      userFetch();
    }
  }, [isAuth, telegramLoading, userFetch]);

  useEffect(() => {
    // Если пользователь загружен и не принял политику конфиденциальности
    if (userLoading) return;

    const currentPath = location.pathname;

    if (!isNavigate && !user?.privacy_policy_accepted && currentPath !== "/sign_up") {
      console.log("isNavigate:", isNavigate)
      console.log("Навигация на /sign_up [TelegramAuth]");
      navigate("/sign_up");
      setIsNavigate(true);
    }
    else if (user?.privacy_policy_accepted && currentPath === "/sign_up") {
      console.log("Навигация на /home [TelegramAuth]");
      navigate("/home");
    }
  }, [user, userLoading, navigate]);

  if (telegramLoading || userLoading) {
    return <AuthLoader />;
  }

  if (!initData) {
    return <NotInTelegram />;
  }

  if (!isAuth) {
    return <TelegramAuthError />;
  }

  // // Если профиль не заполнен, показываем только страницу заполнения
  // if (!user?.privacy_policy_accepted && window.location.pathname !== '/sign_up') {
  //   return null; // или можно вернуть null, так как редирект уже произойдет
  // }

  return <>{children}</>;
}