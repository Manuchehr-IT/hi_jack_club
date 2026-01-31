import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTournamentNearest } from '@/hooks/tournaments/useTournamentNearest';
import Page from '@/components/Page';
import RatingCard from '@/components/RatingCard';
import TournamentCard from '@/components/TournamentCard';
import AboutCard from '@/components/AboutCard';
import GridCard from '@/components/GridCard';
import SocialNetworkCard from '@/components/SocialNetworkCard';
import styles from '@/styles/Home.module.css';

const Home = () => {
  const { tournament, isLoading, error } = useTournamentNearest();
  const navigate = useNavigate();

  const handleSupportClick = () => {
    Telegram.WebApp.openTelegramLink(import.meta.env.VITE_SUPPORT_URL);
  };

  const tournamentNearestCard = tournament ? (
    <div className={styles.section}>
      <h2 className={styles.title}>Ближайший турнир</h2>
      <div key={tournament.id} onClick={() => navigate(`/tournament/${tournament.id}`)}>
        <TournamentCard tournament={tournament} />
      </div>
    </div>
  ) : null;


  return (
    <Page loading={isLoading}>
      <div className={styles.content}>

        {/* Ближайший турнир */}
        {tournamentNearestCard}

        {/* Рейтинг - кликабельный */}
        <div className={styles.section}>
        {/*<div className={styles.section} onClick={() => navigate('/ratings')}>*/}
          <RatingCard />
        </div>

        {/* FAQ и Support */}
        <div className={styles.section}>
          <div className={styles.gridSection}>
            <GridCard title="Вопросы" className={styles.faq} onClick={() => navigate('/faq')} />
            <GridCard title="Помощь" className={styles.support} onClick={handleSupportClick} />
          </div>
        </div>

        {/* О клубе - кликабельный */}
        <div className={styles.section} onClick={() => navigate('/about')}>
          <AboutCard />
        </div>

        <div className={styles.section} onClick={() => navigate('/social-network')}>
          <SocialNetworkCard />
        </div>
      </div>
    </Page>
  );
};

export default Home;