import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useTournamentNearest = () => {
  const [tournament, setTournament] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTournamentNearest = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await api.get(`/tournaments/nearest/`);
        if (response.data) {
          setTournament(response.data);
        } else {
          setTournament(null);
        }
      } catch (err) {
        setError(err.message || "Не удалось загрузить ближайщий турнир");
      } finally {
        setIsLoading(false);
      }
    };

    fetchTournamentNearest();
  }, []);

  return { tournament, isLoading, error };
};
