import { useNavigate } from 'react-router-dom';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useTournamentNearest } from '@/hooks/tournaments/useTournamentNearest';
import { PageLoader } from '@/components/Loaders';
import Footer from '@/components/Footer2';
import RatingCard from '@/components/RatingCard';
import TournamentCard from '@/components/TournamentCard';
import AboutCard from '@/components/AboutCard';
import GridCard from '@/components/GridCard';
import SocialNetworkCard from '@/components/SocialNetworkCard';
import styles from './Home.module.css';

const Home = () => {
  useTelegramBackButton(false);

  const { tournament, isLoading, error } = useTournamentNearest();
  const navigate = useNavigate();

  if (isLoading) return <PageLoader />;

  const handleSupportClick = () => {
    Telegram.WebApp.openTelegramLink(import.meta.env.VITE_SUPPORT_URL);
  };

  return (
    <>
      <main className="container">
        <div className={styles.content}>

          {tournament ? (
            <div className={styles.section}>
              <h2 className={styles.title}>Ближайший турнир</h2>
              <div key={tournament.id} onClick={() => navigate(`/tournament/${tournament.id}`)}>
                <TournamentCard tournament={tournament} />
              </div>
            </div>
          ) : null}

          <div className={styles.section} onClick={() => navigate('/ratings')}>
            <RatingCard />
          </div>

          <div className={styles.section}>
            <div className={styles.gridSection}>
              <GridCard title="Вопросы" className={styles.faq} onClick={() => navigate('/faq')} />
              <GridCard title="Помощь" className={styles.support} onClick={handleSupportClick} />
            </div>
          </div>

          <div className={styles.section} onClick={() => navigate('/about')}>
            <AboutCard />
          </div>

          <div className={styles.section} onClick={() => navigate('/social-network')}>
            <SocialNetworkCard />
          </div>
        </div>
      </main>
      <Footer/>
    </>
  );
};

export default Home;