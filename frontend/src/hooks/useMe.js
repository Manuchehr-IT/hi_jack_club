import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useMe = (enabled = true) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
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

  const updateProfile = useCallback(async (data) => {
    if (!data) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.patch(`/users/update_profile/`, data);
      setUser(prev => ({ ...prev, ...response.data}));
      return response.data;
    } catch (err) {
      setError(err.message || "Не удалось обновить профиль пользователя");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    refetch();
  }, [enabled]);

  return { user, loading, isLoading, error, refetch, updateProfile };
};
