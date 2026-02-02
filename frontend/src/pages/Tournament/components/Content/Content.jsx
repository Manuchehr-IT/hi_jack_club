import { useTournamentRegister } from '@/hooks/tournaments'
import { ContentLoader } from '@/components/Loaders';
import { formatTournamentDate } from '@/utils/formatTournamentDate';
import { hasText } from '@/utils/htmlHelpers';
import InforamtionIcon from '@/assets/icons/information.svg';
import CardSuits from '@/assets/icons/card-suits.svg';
import styles from './Content.module.css';

const Content = ({ tournament }) => {
  const { isRegistered, isLoading, error, checkRegistration, register, unregister } = useTournamentRegister(tournament.id);

  const handleClick = async () => {
    if (isLoading) return;

    if (isRegistered) {
      await unregister();
    } else {
      await register();
    }
  };

  return (
    <main className="container">
      <section className={styles.tabsSection}>
        <button className={`${styles.button} ${styles.participation}`} onClick={handleClick} disabled={isLoading}>
          <span className={styles.text}>
            {
              isLoading ? (
                <ContentLoader />
              ) : (
                isRegistered ? "Отменить запись" : "Участвовать"
              )
            }
          </span>
        </button>

        <button className={`${styles.button} ${styles.info}`}>
          <img src={CardSuits} alt="card-suits" className={styles.icon} />
          <p className={styles.text}>О турнире</p>
        </button>
      </section>

      <section className={styles.infoSection}>
        <h2 className={styles.title}>Когда и где</h2>
        <div className={styles.detailsGrid}>
          <div className={styles.detailItem}>
            <img src="https://app.check-checkclub.ru/images/icons/location-pin-icon.svg" alt="Локация" className={styles.icon} />
            <p className={styles.text}>{tournament.location}</p>
          </div>
          <div className={styles.detailItem}>
            <img src="https://app.check-checkclub.ru/images/icons/time-icon.svg" alt="Время" className={styles.icon} />
            <p className={styles.text}>{formatTournamentDate(tournament.started_at)}</p>
          </div>
        </div>

        <h2 className={styles.title}>Общие правила</h2>
        <p className={styles.text}>{tournament.general_rules || "Правила не указаны."}</p>

        <h2 className={styles.title}>Особенности</h2>
        {tournament.features && tournament.features.length > 0 && (
          <ul className={styles.featuresList}>
            {tournament.features.map((feature, index) => (
              <li key={index} className={styles.text}>{feature}</li>
            ))}
          </ul>
        ) || (<p className={styles.text}>Особенности не указаны</p>)}

      </section>

      <section className={styles.footerSection}>
        <div className={styles.hintCard}>
          <div className={styles.cardContent}>
            <div className={styles.detailItem}>
              <img src={InforamtionIcon} alt="InforamtionIcon" className={styles.icon}/>
              <h4 className={styles.title}>Запись на турниры</h4>
            </div>
            <ul className={styles.hints}>
              <li className={styles.text}>По нашим правилам гости должны заблаговременно отменять регистрацию, чтобы не забирать место у желающих из очереди.</li>
            </ul>
          </div>
        </div>
      </section>

    </main>
  );
};

export default Content;