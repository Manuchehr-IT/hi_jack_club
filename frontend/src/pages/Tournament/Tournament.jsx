import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useTournament } from '@/hooks/useTournament';
import Page from '@/components/Page';
import Header from '@/components/tournament/Header';
import Buttons from '@/components/tournament/Buttons';
import Info from '@/components/tournament/Info';
import styles from './Tournament.module.css';

const Tournament = () => {
  useTelegramBackButton(true);

  const { id } = useParams();
  const { tournament, loading, error } = useTournament(id);

  // TODO page
  // Если ошибка загрузки турнира
  // if (!loading.tournament && error) {
  //   return (
  //     <div className={styles.errorPage}>
  //       <h1 className={styles.errorTitle}>Ошибка загрузки</h1>
  //       <p className={styles.errorMessage}>{error}</p>
  //       <div className={styles.errorActions}>
  //         <button onClick={() => window.location.reload()} className={styles.retryButton}>Обновить страницу</button>
  //         <a href="/tournaments" className={styles.backLink}>← К списку турниров</a>
  //       </div>
  //     </div>
  //   );
  // }

  return (
    <Page loading={loading}>
      <Header tournament={tournament} />
      <Buttons tournament={tournament} />
      <Info tournament={tournament} />
    </Page>
  );
};

export default Tournament;