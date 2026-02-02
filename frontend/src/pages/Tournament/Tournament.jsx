import { useParams } from 'react-router-dom';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useTournament } from '@/hooks/tournaments'
import { PageLoader } from '@/components/Loaders';
import { formatTournamentDate } from '@/utils/formatTournamentDate';
import { hasText } from '@/utils/htmlHelpers';
import EllipseIcon from '@/assets/icons/ellipse.svg';
import Footer from '@/components/Footer2';
import { Header, Content } from './components'
import styles from './Tournament.module.css';

const Tournament = () => {
  useTelegramBackButton(true);

  const { id } = useParams();
  const { tournament, isLoading, error: tournamentError } = useTournament(id);

  if (isLoading) return <PageLoader />;

  return (
    <>
      <Header tournament={tournament}/>
      <Content tournament={tournament}/>
      <Footer/>
    </>
  );
};

export default Tournament;