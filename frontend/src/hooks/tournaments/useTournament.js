import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useTournament = (tournamentId) => {
  const [tournament, setTournament] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTournament = useCallback(async () => {
    if (!tournamentId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get(`/tournaments/${tournamentId}/`);
      setTournament(response.data);
      return response.data;
    } catch (err) {
      setError(err.message || "Не удалось загрузить информацию о турнире");
    } finally {
      setIsLoading(false);
    }
  }, [tournamentId]);

  useEffect(() => {
    if (tournamentId) {
      fetchTournament();
    }
  }, [tournamentId, fetchTournament]);

  return { tournament, isLoading, error, fetchTournament };
};
