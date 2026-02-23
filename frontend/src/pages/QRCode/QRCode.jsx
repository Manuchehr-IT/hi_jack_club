import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton';
import { useMe } from "@/hooks/useMe";
import { useTournamentTodayStatus } from "@/hooks/tournaments/useTournamentTodayStatus";
import { PageLoader } from '@/components/Loaders';
import Footer from '@/components/Footer2';
import styles from './QRCode.module.css';

const QRCode = () => {
  useTelegramBackButton(false);

  const { user, loading, error } = useMe();
  const { tournamentStatusData, isLoading, error: tournamentTodayStatusError } = useTournamentTodayStatus();

  if (loading && isLoading) return <PageLoader/>;

  const tournament_title = tournamentStatusData?.title;
  const participant_status = tournamentStatusData
    ? (
      tournamentStatusData.status == "REGISTERED" ? 1 : 2
    ) : null;

  const qrCode = user?.iiko_qr_code;

  if (!loading && !qrCode) {
    return (
      <>
        <main className="container">
          <div className={styles.error}>
            QR-код ещё не сгенерирован
          </div>
        </main>
        <Footer/>
      </>
    );
  }

  return (
    <>
      <main className="container">
        <div className={styles.content}>
          <h1 className={styles.title}>Ваш QR-код</h1>
          <p className={styles.subtitle}>Покажите его сотруднику для сканирования</p>

          <div className={styles.card}>
            <img src={qrCode} alt="QR Code" className={styles.qr}/>
          </div>
          {tournamentStatusData && <span className={styles.tournamentHint}>{tournament_title} - {participant_status}</span>}
        </div>
      </main>
      <Footer/>
    </>
  );
};

export default QRCode;
