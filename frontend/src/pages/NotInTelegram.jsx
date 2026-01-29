function NotInTelegram() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      textAlign: 'center',
      padding: '20px'
    }}>
      <div>
        <h1>🚫 Приложение доступно только в Telegram</h1>
        <p>Это приложение предназначено для запуска внутри Telegram как Mini App.</p>
        <p>Откройте приложение через Telegram бота или по ссылке в Telegram.</p>
      </div>
    </div>
  );
}

export default NotInTelegram;