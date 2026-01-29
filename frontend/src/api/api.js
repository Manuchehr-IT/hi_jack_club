import axios from 'axios';

console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
console.log('All env:', import.meta.env);

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true",
  }
});

// ⬇️ Сохранение нового токена из ответа
// api.interceptors.response.use(
//   (response) => {
//     const authHeader = response.headers["authorization"];
//       console.log("authHeader:", authHeader);
//     if (authHeader && authHeader.startsWith("Bearer ")) {
//       const token = authHeader.split(" ")[1];
//       console.log("new token:", token);
//       localStorage.setItem("access_token", token);
//     }

//     // const tokenFromHeader = response.headers["access_token"];
//     // const tokenFromBody = response.data?.token;
//     // const token = tokenFromHeader || tokenFromBody;

//     // if (token) {
//     //   localStorage.setItem("access_token", token);

//     //   // Если токен был в теле ответа, удаляем его чтобы не мешал
//     //   if (tokenFromBody && response.data) {
//     //     delete response.data.token;
//     //   }
//     // }

//     return response;
//   },
//   (error) => {
//     let message = "Неизвестная ошибка";

//     if (error.response) {
//       message = error.response.data?.message || `Ошибка ${error.response.status}`;
//     } else if (error.request) {
//       message = 'Сервер не отвечает';
//     } else {
//       message = error.message;
//     }

//     console.error('API Error:', message, error);

//     return Promise.reject(new Error(message));
//   }
// );

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