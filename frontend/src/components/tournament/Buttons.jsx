import { ContentLoader, AuthLoader } from '@/components/Loaders';
import { useTournamentRegister } from '@/hooks/tournaments/useTournamentRegister'
import CardSuits from '@/assets/icons/card-suits.svg';
import styles from '@/styles/tournament/Buttons.module.css';

const Buttons = ({ tournament }) => {
  const { isRegistered, isLoading, error, checkRegistration, register, unregister } = useTournamentRegister(tournament.id);

  const handleClick = async () => {
    if (isLoading) return;

    if (isRegistered) {
      await unregister();
    } else {
      await register();
    }
  };

  const getButtonText = () => {
    if (isLoading) {
      return <ContentLoader />;
    }

    return isRegistered ? "Отменить участие" : "Участвовать";
  };

  return (
    <div className={styles.container}>
      <button className={`${styles.button} ${styles.participation}`} onClick={handleClick} disabled={isLoading}>
        <span className={styles.text}>{getButtonText()}</span>
      </button>

      <button className={`${styles.button} ${styles.info}`}>
        <img src={CardSuits} alt="card-suits" className={styles.icon} />
        <p className={styles.text}>О турнире</p>
      </button>
    </div>
  );
};

export default Buttons;
