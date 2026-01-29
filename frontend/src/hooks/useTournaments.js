import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useTournaments = () => {
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        const response = await api.get(`/tournaments/`);
        const tournamentsData = response.data || [];
        setTournaments(Array.isArray(tournamentsData) ? tournamentsData : []);
      } catch (err) {
        setError(err.message || "Не удалось загрузить список турниров");
      } finally {
        setLoading(false);
      }
    };

    fetchTournaments();
  }, []);

  return { tournaments, loading, error };
};
