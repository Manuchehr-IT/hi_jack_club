import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useUsers = () => {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = { ordering: "-rating" };
      const response = await api.get(`/users/`, { params });
      const usersData = response.data;
      setUsers(Array.isArray(usersData) ? usersData : []);
    } catch (err) {
      console.error("Ошибка загрузки пользователя:", err);
      setError(err.message || "Не удалось загрузить информацию о пользователях");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return { users, isLoading, error };
};
