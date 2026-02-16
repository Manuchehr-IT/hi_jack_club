import { useState, useEffect, useCallback } from 'react';
import api from '@/api/api';

export const useSignUp = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const signUp = useCallback(async (data) => {
    if (!data) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.patch(`/users/sign_up/`, data);
      return response.data;
    } catch (err) {
      console.log({err})
      if (err.response?.status === 400) {
        if (err.response.data?.code === "incorrect_phone_format") {
          setError("Недопустимый формат телефона");
        } else if (err.response.data?.nickname) {
          setError("Этот никнейм уже занят")
        }
      } else if (err.response?.status === 422) {
        if (err.response?.data?.code === "invalid_phone_number") {
          setError("Недопустимый номер телефона");
        }
        else if (err.response?.data.code === "incorrect_nickname_length") {
          setError("Длина никнейма не может быть менее 3 или более 32 символов")
        }
      } else if (err.response?.status === 409) {
        if (err.response?.data?.code == "phone_already_taken") {
          setError("Этот номер телефона уже используется")
        } else if (err.response?.data?.code == "nickname_already_taken") {
          setError("Этот никнейм уже занят")
        }
      // } else {
      } else if (err.response?.data) {
        setError(`Ошибка: ${JSON.stringify(err.response.data, null, 2)}`)
      } else {
        setError(`Неизвестная ошибка: ${err.response.message}`)
        setError(err.message || "Не удалось зарегистрировать пользователя");
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, signUp };
};
