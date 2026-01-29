import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useSignUp = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const signUp = useCallback(async (data) => {
    if (!data) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.patch(`/users/sign_up/`, data);
      return response.data;
    } catch (err) {
      setError(err.message || "Не удалось зарегистрировать пользователя");
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, signUp };
};
