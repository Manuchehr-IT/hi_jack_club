import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useTournamentRegister = (tournamentId) => {
  const [registrationStatus, setRegistrationStatus] = useState(null);
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

  const checkRegistrationStatus = useCallback(async () => {
    if (!tournamentId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get(`/tournaments/${tournamentId}/registration-status/`);
      setRegistrationStatus(response.data.status);
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
      setRegistrationStatus(response.data.status);
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
      setRegistrationStatus(null);
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
      checkRegistrationStatus(tournamentId);
    }
  }, [tournamentId, checkAvailability, checkRegistrationStatus]);

  return { availability, registrationStatus, isLoading, error, checkRegistrationStatus, register, unregister };
};
