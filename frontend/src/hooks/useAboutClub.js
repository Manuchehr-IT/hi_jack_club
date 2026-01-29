import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useAboutClub = () => {
  const [aboutClub, setAboutClub] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchallAboutClub = async () => {
      try {
        const response = await api.get(`/about_club/`);
        const aboutClubData = response.data || [];
        setAboutClub(Array.isArray(aboutClubData) ? aboutClubData : []);
      } catch (err) {
        setError(err.message || "Не удалось загрузить список блоков 'О клубе'");
      } finally {
        setLoading(false);
      }
    };

    fetchallAboutClub();
  }, []);

  return { aboutClub, loading, error };
};
