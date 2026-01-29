import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useSocialNetwork = () => {
  const [socialNetwork, setSocialNetwork] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSocialNetwork = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await api.get(`/social-network/as_dict/`);
        const data = response.data || {};
        setSocialNetwork(data);
      } catch (err) {
        setError(err.message || "Не удалось загрузить словарь соцсетей");
      } finally {
        setLoading(false);
      }
    };

    fetchSocialNetwork();
  }, []);

  return { socialNetwork, loading, error };
};
