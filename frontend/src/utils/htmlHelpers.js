/**
 * Проверяет, содержит ли HTML реальный текст (не только теги и пробелы)
 * @param {string} html - HTML строка для проверки
 * @returns {boolean} true если есть видимый текст
 */
export const hasText = (html) => {
  if (!html || html.trim() === '') return false;

  const cleanText = html
    .replace(/<[^>]*>/g, '')                    // удаляем все HTML теги
    .replace(/&nbsp;|&#160;/gi, ' ')            // заменяем неразрывные пробелы
    .replace(/&[a-z0-9]+;/gi, '')               // удаляем все другие HTML-сущности
    .replace(/\s+/g, '')                        // удаляем все оставшиеся пробелы
    .trim();

  return cleanText.length > 0;
};

/**
 * Очищает HTML от тегов, оставляя только текст
 * @param {string} html - HTML строка
 * @returns {string} чистый текст
 */
export const stripHtml = (html) => {
  if (!html) return '';
  
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;|&#160;/gi, ' ')
    .replace(/&[a-z0-9]+;/gi, '')
    .replace(/\s+/g, ' ')
    .trim();
};

/**
 * Безопасно обрезает HTML текст до указанной длины
 * @param {string} html - HTML строка
 * @param {number} maxLength - максимальная длина
 * @returns {string} обрезанный текст с многоточием
 */
export const truncateHtmlText = (html, maxLength = 100) => {
  const text = stripHtml(html);
  if (text.length <= maxLength) return text;
  
  return text.substring(0, maxLength) + '...';
};