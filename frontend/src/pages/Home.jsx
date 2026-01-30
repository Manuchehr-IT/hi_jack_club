import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Page from '@/components/Page';
import RatingCard from '@/components/RatingCard';
import TournamentCard from '@/components/TournamentCard';
import AboutCard from '@/components/AboutCard';
import GridCard from '@/components/GridCard';
import SocialNetworkCard from '@/components/SocialNetworkCard';
import styles from '@/styles/Home.module.css';

const Home = () => {
  const navigate = useNavigate();
  // const loading = true;

  // Данные турнира
  const upcomingTournament = {
    id: 5,
    title: 'HI, LADIES!',
    started_at: '2025-12-24T23:05:16.148338+03:00',
    image: '/images/chips/isometric/cards.png'
  };

  const handleSupportClick = () => {
    Telegram.WebApp.openTelegramLink(import.meta.env.VITE_SUPPORT_URL);
    // window.open("https://t.me/async_io", "_blank");
  };

  return (
    <Page>
      <div className={styles.content}>

        {/* Ближайший турнир */}
        <div className={styles.section}>
          <h2 className={styles.title}>Ближайший турнир</h2>
          <div onClick={() => navigate(`/tournament/${upcomingTournament.id}`)}>
            <TournamentCard tournament={upcomingTournament} />
          </div>
        </div>

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