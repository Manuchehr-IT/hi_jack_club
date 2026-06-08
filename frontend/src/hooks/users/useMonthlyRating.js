import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useMonthlyRating = (month) => {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMonthlyRating = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get('/users/monthly_rating/', { params: { month } });
      setUsers(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Ошибка загрузки месячного рейтинга:', err);
      setError(err.message || 'Не удалось загрузить рейтинг');
    } finally {
      setIsLoading(false);
    }
  }, [month]);

  useEffect(() => {
    fetchMonthlyRating();
  }, [fetchMonthlyRating]);

  return { users, isLoading, error };
};
