import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useUsers = (userId) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Загрузка информации о пользователе
  // const fetchUser = useCallback(async () => {
  useEffect(() => {
    if (!userId) return; // Данная проверка вообще нужна? функция вроде не сработает же без получения требуемого параметра userId?

    try {
      const response = await api.get(`/users/me/`);

      // Проверяем статус ответа
      if (response.status === 404) {
        throw new Error("Пользователь не найден");
      }

      if (response.status >= 400) {
        const errorData = response.data || {};
        throw new Error(errorData.message || `Ошибка ${response.status}`);
      }

      setUser(response.data);

    } catch (err) {
      console.error("Ошибка загрузки пользователя:", err);
      setError(err.message || "Не удалось загрузить информацию о пользователе");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  return { user, loading, error };
};
