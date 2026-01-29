import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useTournamentRegister = (tournamentId) => {
  const [isRegistered, setIsRegistered] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const checkRegistration = useCallback(async () => {
    if (!tournamentId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get(`/tournaments/${tournamentId}/registration-status/`);
      setIsRegistered(response.data.is_registered);
      return response.data.is_registered;
    } catch (err) {
      setError(err.message || "Не удалось проверить участие в турнире");
    } finally {
      setIsLoading(false);
    }
  }, [tournamentId]);

  const register = useCallback(async () => {
    if (!tournamentId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post(`/tournaments/${tournamentId}/register/`);
      setIsRegistered(true);
      return true;
    } catch (err) {
      setError(err.message || "Не удалось принять участие в турнире");
    } finally {
      setIsLoading(false);
    }
  }, [tournamentId]);

  const unregister = useCallback(async () => {
    if (!tournamentId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.delete(`/tournaments/${tournamentId}/unregister/`);
      setIsRegistered(false);
      return false;
    } catch (err) {
      setError(err.message || "Не удалось отменить участие в турнире");
    } finally {
      setIsLoading(false);
    }
  }, [tournamentId]);

  useEffect(() => {
    if (tournamentId) {
      checkRegistration(tournamentId);
    }
  }, [tournamentId, checkRegistration]);

  return { isRegistered, isLoading, error, checkRegistration, register, unregister };
};
