import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useFAQ = () => {
  const [FAQ, setFAQ] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchallFAQ = async () => {
      try {
        const response = await api.get(`/faq/`);
        const FAQData = response.data || [];
        setFAQ(Array.isArray(FAQData) ? FAQData : []);
      } catch (err) {
        setError(err.message || "Не удалось загрузить список вопрос-ответов");
      } finally {
        setLoading(false);
      }
    };

    fetchallFAQ();
  }, []);

  return { FAQ, loading, error };
};
