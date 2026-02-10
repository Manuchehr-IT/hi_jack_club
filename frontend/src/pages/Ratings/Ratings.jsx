import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useUsers } from '@/hooks/users/useUsers';
import { PageLoader } from '@/components/Loaders';
import Footer from '@/components/Footer2';
import styles from './Ratings.module.css';

const Ratings = () => {
  useTelegramBackButton(true);

  const { users, isLoading, error } = useUsers();

  if (isLoading) return <PageLoader/>;

  return (
    <main>
      <div className={styles.header}>
        <h1 className={styles.title}>Рейтинг Hi, Jack Club!</h1>
      </div>

      {/* Таблица рейтингов */}
      <div className={styles.table}>
        {/* Заголовки таблицы */}
        <div className={styles.tableHeader}>
          <div className={styles.headerCell}></div>
          <div className={`${styles.headerCell} ${styles.headerNickname}`}>Никнейм</div>
          <div className={`${styles.headerCell} ${styles.headerRight}`}>Нокауты</div>
          <div className={`${styles.headerCell} ${styles.headerRight}`}>Рейтинг</div>
        </div>

        {/* Строки таблицы */}
        <div className={styles.tableBody}>
          {users.map((user, index) => (
            <div key={user.id} className={styles.tableRow}>
              <div className={styles.positionCell}>
                <span className={styles.positionNumber}>#{index +1}</span>
              </div>

              <div className={styles.nicknameCell}>
                <span className={styles.userName}>{user.nickname}</span>
              </div>

              <div className={styles.knockoutsCell}>
                <span className={styles.statValue}>{user.knockouts}</span>
              </div>

              <div className={styles.ratingCell}>
                <span className={styles.ratingValue}>{user.rating}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      <Footer/>
    </main>
  );
};

export default Ratings;