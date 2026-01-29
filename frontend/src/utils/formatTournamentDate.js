export const formatTournamentDate = (iso) => {
  if (!iso) return '';

  const d = new Date(iso);

  const dayMonth = d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
  });

  const weekday = d.toLocaleDateString('ru-RU', {
    weekday: 'short',
  }).replace('.', '');

  const time = d.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

  return `${dayMonth}, ${weekday} / ${time}`;
};
