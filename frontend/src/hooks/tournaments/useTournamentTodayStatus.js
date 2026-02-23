import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useTournamentTodayStatus = () => {
  const [tournamentStatusData, setTournamentStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTournamentTodayStatus = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await api.get(`/tournaments/today-status/`);
        if (response.data) {
          setTournamentStatus(response.data);
        } else {
          setTournamentStatus(null);
        }
      } catch (err) {
        setError(err.message || "Не удалось загрузить статус сегоднящнего турнира");
      } finally {
        setIsLoading(false);
      }
    };

    fetchTournamentTodayStatus();
  }, []);

  return { tournamentStatusData, isLoading, error };
};
