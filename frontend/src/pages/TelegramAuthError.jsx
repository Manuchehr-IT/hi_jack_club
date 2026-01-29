import React from 'react';

function TelegramAuthError() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      textAlign: 'center',
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <h1 style={{ fontSize: '24px' }}>🚫 Ошибка авторизации</h1>
        <p style={{ fontSize: '16px' }}>Попробуйте перезапустить Telegram Mini App.</p>
        <p style={{ fontSize: '16px' }}>Тех.поддержка: @async_io</p>
      </div>
    </div>
  );
}

export default TelegramAuthError;