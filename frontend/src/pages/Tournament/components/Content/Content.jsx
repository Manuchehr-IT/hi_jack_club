import { useTournamentRegister } from '@/hooks/tournaments'
import { ContentLoader } from '@/components/Loaders';
import { formatTournamentDate } from '@/utils/formatTournamentDate';
import { hasText } from '@/utils/htmlHelpers';
import InforamtionIcon from '@/assets/icons/information.svg';
import CardSuits from '@/assets/icons/card-suits.svg';
import styles from './Content.module.css';

const Content = ({ tournament }) => {
  const { availability, registrationData, isLoading, error, checkRegistrationData, register, unregister } = useTournamentRegister(tournament.id);

  const registrationStatus = registrationData?.status
  const isRegistrationAvailable = availability && (availability.registrations > 0 || availability.waitlists > 0);

  const buttonText = (() => {
    if (registrationStatus) return "Отменить запись";
    if (!isRegistrationAvailable) return "Нет мест";
    if (availability.registrations > 0) return "Участвовать";
    if (availability.waitlists > 0) return "В список ожидания";
  })();

  const hintTitle = (() => {
    if (tournament.status !== "IN_QUEUE") return null;
    if (error) return error;
    if (!registrationStatus) return "Запись на турниры.";
    if (registrationStatus === "WAITLIST") return "Вы в списке ожидания.";
    return null;
  })();

  const hintTexts = (() => {
    if (tournament.status !== "IN_QUEUE") return null;
    if (error) return null;
    if (!registrationStatus) return ["По нашим правилам гости должны заблаговременно отменять регистрацию, чтобы не забирать место у желающих из очереди."];
    if (registrationStatus === "WAITLIST") return [
      `Вы в списке ожидания на ${registrationData.waitlist_position} месте`,
      "Как только освободится место, мы автоматически добавим вас в основной список."
    ];
    return null;
  })();

  const handleClick = async () => {
    if (isLoading) return;

    if (registrationStatus) {
      await unregister();
    } else {
      await register();
    }
  };

  return (
    <main className="container">
      <section className={styles.tabsSection}>
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
        <p className={styles.text}>
          {/*<Linkify options={{target: "_blank", rel: "noopener noreferrer"}}>*/}
          {tournament.general_rules || "Правила не указаны."}
          {/*</Linkify>*/}
        </p>

        <h2 className={styles.title}>Особенности</h2>
        {tournament.features && tournament.features.length > 0 && (
          <ul className={styles.featuresList}>
            {tournament.features.map((feature, index) => (
              <li key={index} className={styles.text}>{feature}</li>
            ))}
          </ul>
        ) || (<p className={styles.text}>Особенности не указаны</p>)}

      </section>

      {tournament.status === "IN_QUEUE" ? (
        <section className={styles.registerSection}>
          <button className={`${styles.button} ${styles.participation}`} onClick={handleClick} disabled={isLoading || !!error || (!isRegistrationAvailable && !registrationStatus)}>
            <span className={styles.text}>
              {isLoading ? <ContentLoader /> : buttonText}
            </span>
          </button>
        </section>
        ): null}

      {hintTitle ? (
        <section className={styles.footerSection}>
          <div className={styles.hintCard}>
            <div className={styles.cardContent}>
              <div className={styles.detailItem}>
                <img src={InforamtionIcon} alt="InforamtionIcon" className={styles.icon}/>
                <h4 className={styles.title}>{hintTitle}</h4>
              </div>
              {hintTexts ? (
                <ul className={styles.hints}>
                  {hintTexts.map((hintText, index) => (
                    <li key={index} className={styles.text}>{hintText}</li>
                  ))}
                </ul>
              ): null}
            </div>
          </div>
        </section>
      ) : null}

    </main>
  );
};

export default Content;