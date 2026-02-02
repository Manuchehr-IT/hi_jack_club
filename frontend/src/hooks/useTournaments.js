import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useTournaments = () => {
  const [tournaments, setTournaments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        const params = { status: "IN_QUEUE" };
        const response = await api.get(`/tournaments/`, { params });
        const tournamentsData = response.data;
        setTournaments(Array.isArray(tournamentsData) ? tournamentsData : []);
      } catch (err) {
        setError(err.message || "Не удалось загрузить список турниров");
      } finally {
        setIsLoading(false);
      }
    };

    fetchTournaments();
  }, []);

  return { tournaments, isLoading, error };
};
