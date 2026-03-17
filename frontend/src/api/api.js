import axios from 'axios';

console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
console.log('All env vars:', import.meta.env);

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  // withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true",
  }
});


api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (status === 401) {
      console.log("Ошибка авторизации [api.interceptors.response.use]");
    }

    return Promise.reject(error)
  }
);

// ⬆️ Вставка токена в запрос
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
}, (error) => {
  return Promise.reject(error);
});

// Вспомогательные функции для работы с токеном
export const tokenService = {
  getToken: () => localStorage.getItem("access_token"),
  setToken: (token) => localStorage.setItem("access_token", token),
  removeToken: () => localStorage.removeItem("access_token"),
  hasToken: () => !!localStorage.getItem("access_token")
};

export default api;