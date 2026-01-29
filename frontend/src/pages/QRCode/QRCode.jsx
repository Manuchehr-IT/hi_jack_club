import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMe } from "@/hooks/useMe";
import Page from '@/components/Page';
import styles from './QRCode.module.css';

// const QRCode = () => {
//   const { user, loading: userLoading, error: userError, refetch: userFetch } = useMe();
//   const qr_code = user?.iiko_qr_code

//   // Добавлю ошибку если qr_code будет null.

//   return (
//     <Page loading={userLoading}>
//       <img src={qr_code} />
//     </Page>
//   );
// };

const QRCode = () => {
  const { user, loading, error } = useMe();

  const qrCode = user?.iiko_qr_code;

  if (!loading && !qrCode) {
    return (
      <Page>
        <div className={styles.error}>
          QR-код ещё не сгенерирован
        </div>
      </Page>
    );
  }

  return (
    <Page loading={loading}>
      <div className={styles.wrapper}>
        <h1 className={styles.title}>Ваш QR-код</h1>
        <p className={styles.subtitle}>Покажите его сотруднику для сканирования</p>

        <div className={styles.card}>
          <img
            src={qrCode}
            alt="QR Code"
            className={styles.qr}
          />
        </div>
      </div>
    </Page>
  );
};

export default QRCode;
