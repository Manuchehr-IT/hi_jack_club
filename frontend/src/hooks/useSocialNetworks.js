import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useSocialNetworks = () => {
  const [socialNetworks, setSocialNetworks] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSocialNetworks = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await api.get(`/social-network/as_dict/`);
        const data = response.data || {};
        setSocialNetworks(data);
      } catch (err) {
        setError(err.message || "Не удалось загрузить словарь соцсетей");
      } finally {
        setIsLoading(false);
      }
    };

    fetchSocialNetworks();
  }, []);

  return { socialNetworks, isLoading, error };
};
