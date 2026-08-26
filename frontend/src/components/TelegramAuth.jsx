import { useEffect, useState } from 'react';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import { useTelegramAuth } from '@/hooks/useTelegramAuth';
import { useMe } from '@/hooks/useMe';
import { AuthLoader } from '@/components/Loaders';
import NotInTelegram from '@/pages/NotInTelegram';
import TelegramAuthError from '@/pages/TelegramAuthError';
import api from '@/api/api';
import { consumePendingRedirect } from '@/utils/deepLink';

export default function TelegramAuth({ children }) {
  const { initData, loading: telegramLoading, isAuth } = useTelegramAuth();
  const { refetch: userFetch } = useMe(false);
  const [isSigned, setIsSigned] = useState(false)
  const navigate = useNavigate();
  const location = useLocation();

  const navigateToSignUp = () => {
    if (location.pathname === "/sign_up") {
      return;
    }

    console.log("Навигация на /sign_up [TelegramAuth]");
    navigate("/sign_up", { replace: true });
  }

  // const navigateToHome = () => {
  //   console.log("Навигация на /home [TelegramAuth]");
  //   navigate("/home", { replace: true });
  //   setIsSigned(true);
  // }

  const handleNavigation = async () => {
    const user = await userFetch();
    console.log("TelegramAuth:", {user})
    if (user?.privacy_policy_accepted) {
      const redirectPath = consumePendingRedirect();
      if (redirectPath) {
        console.log("Навигация на диплинк [TelegramAuth]:", redirectPath);
        navigate(redirectPath, { replace: true });
      }
      setIsSigned(true);
    } else {
      navigateToSignUp();
    }
  }

  useEffect(() => {
    if (!telegramLoading && initData && isAuth && !isSigned) {
      handleNavigation();
    }
  }, [telegramLoading, initData, isAuth, isSigned, navigate]);

  if (telegramLoading) {
    return <AuthLoader />;
  }

  if (!initData) {
    return <NotInTelegram />;
  }

  if (!isAuth) {
    return <TelegramAuthError />;
  }

  return <>{children}</>;
}
