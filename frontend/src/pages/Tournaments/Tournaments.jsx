import { useNavigate } from 'react-router-dom';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useTournaments } from '@/hooks/useTournaments';
import { PageLoader } from '@/components/Loaders';
import Footer from '@/components/Footer2';
import TournamentCard from '@/components/TournamentCard';
import styles from './Tournaments.module.css';

const Tournaments = () => {
  useTelegramBackButton(false);

  const { tournaments, isLoading, error } = useTournaments();
  const navigate = useNavigate();

  if (isLoading) return <PageLoader />;

  return (
    <>
      <main className="container">
        <div className={styles.content}>
          {tournaments.map((tournament) => (
            <div key={tournament.id} onClick={() => navigate(`/tournament/${tournament.id}`)}>
              <TournamentCard tournament={tournament} />
            </div>
          ))}
        </div>
      </main>
      <Footer/>
    </>
  );
};

export default Tournaments;
