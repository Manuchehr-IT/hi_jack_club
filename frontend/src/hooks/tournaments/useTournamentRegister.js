import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useTournamentRegister = (tournamentId) => {
  const [registrationData, setRegistrationData] = useState(null);
  const [availability, setAvailability] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const checkAvailability = useCallback(async () => {
    if (!tournamentId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get(`/tournaments/${tournamentId}/availability/`);
      setAvailability(response.data);
    } catch (err) {
      setError(err.message || "Не удалось получить данные о доступности турнира");
    } finally {
      setIsLoading(false);
    }
  }, [tournamentId]);

  const checkRegistrationData = useCallback(async () => {
    if (!tournamentId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get(`/tournaments/${tournamentId}/registration-status/`);
      setRegistrationData(response.data);
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
      setRegistrationData(response.data);
      checkAvailability();
    } catch (err) {
      if (err.response?.status === 400) {
        setError(err.response.data.detail);
      } else {
        setError(err.message || "Не удалось принять участие в турнире");
      };
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
      setRegistrationData(null);
      checkAvailability();
    } catch (err) {
      if (err.response?.status === 400) {
        setError(err.response.data.detail);
      } else {
        setError(err.message || "Не удалось отменить участие в турнире");
      }
    } finally {
      setIsLoading(false);
    }
  }, [tournamentId]);

  useEffect(() => {
    if (tournamentId) {
      checkAvailability(tournamentId);
      checkRegistrationData(tournamentId);
    }
  }, [tournamentId, checkAvailability, checkRegistrationData]);

  return { availability, registrationData, isLoading, error, checkRegistrationData, register, unregister };
};
