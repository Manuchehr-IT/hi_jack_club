const STORAGE_KEY = "pending_redirect";
const TOURNAMENT_START_PARAM = /^tournament_(\d+)$/;

/**
 * Преобразует Telegram start_param (из ссылки t.me/<bot>/<app>?startapp=...)
 * в путь внутри приложения, если он указывает на турнир.
 */
export function resolveStartParamPath(startParam) {
  if (!startParam) return null;

  const match = TOURNAMENT_START_PARAM.exec(startParam);
  if (!match) return null;

  return `/tournament/${match[1]}`;
}

export function setPendingRedirect(path) {
  try {
    sessionStorage.setItem(STORAGE_KEY, path);
  } catch {
    // sessionStorage может быть недоступен (приватный режим и т.п.) — диплинк просто не сработает
  }
}

/**
 * Возвращает сохранённый путь для редиректа и сразу его удаляет,
 * чтобы повторный рендер не редиректил снова.
 */
export function consumePendingRedirect() {
  try {
    const path = sessionStorage.getItem(STORAGE_KEY);
    if (path) sessionStorage.removeItem(STORAGE_KEY);
    return path;
  } catch {
    return null;
  }
}
