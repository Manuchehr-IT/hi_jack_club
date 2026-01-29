import styles from '@/styles/Ratings.module.css';

const Ratings = () => {
  const ratings = [
    { id: 1, position: 1, name: 'PlayerOne', points: 1500, knockouts: 10 },
    { id: 2, position: 2, name: 'PlayerTwo', points: 1450, knockouts: 5 },
    { id: 3, position: 3, name: 'PlayerThree', points: 1400, knockouts: 25 },
    { id: 4, position: 4, name: 'PlayerFour', points: 1350, knockouts: 15 },
    { id: 5, position: 5, name: 'PlayerFive', points: 1300, knockouts: 8 },
  ];

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <h1 className={styles.title}>Рейтинг Hi, Jack Club!</h1>
      </div>

      {/* Таблица рейтингов */}
      <div className={styles.table}>
        {/* Заголовки таблицы */}
        <div className={styles.tableHeader}>
          <div className={styles.headerCell}></div>
          <div className={`${styles.headerCell} ${styles.headerName}`}>Никнейм</div>
          <div className={`${styles.headerCell} ${styles.headerRight}`}>Нокауты</div>
          <div className={`${styles.headerCell} ${styles.headerRight}`}>Рейтинг</div>
        </div>

        {/* Строки таблицы */}
        <div className={styles.tableBody}>
          {ratings.map((player) => (
            <div key={player.id} className={styles.tableRow}>
              <div className={styles.positionCell}>
                <span className={styles.positionNumber}>#{player.position}</span>
              </div>
              
              <div className={styles.nameCell}>
                <span className={styles.playerName}>{player.name}</span>
              </div>
              
              <div className={styles.knockoutsCell}>
                <span className={styles.statValue}>{player.knockouts}</span>
              </div>
              
              <div className={styles.ratingCell}>
                <span className={styles.ratingValue}>{player.points}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Ratings;