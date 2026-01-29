import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useMe = (enabled = true) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get(`/users/me/`);
      setUser(response.data);
      return response.data;
    } catch (err) {
      setError(err.message || "Не удалось загрузить информацию о пользователе");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    refetch();
  }, [enabled]);

  return { user, loading, error, refetch };
};
