// src/components/tournament/Info.jsx
import React from 'react';
import CardSuits from '@/assets/icons/card-suits.svg';
import styles from '@/styles/tournament/Info.module.css';
import { formatTournamentDate } from '@/utils/formatTournamentDate';
import { hasText } from '@/utils/htmlHelpers';

const Info = ({ tournament }) => {
  return (
    <div className={styles.content}>

      {/* Когда и где */}
      <section className={styles.section}>
        <h2 className={styles.title}>Когда и где</h2>
        <div className={styles.detailsGrid}>
          <div className={styles.detailItem}>
            <img src="https://app.check-checkclub.ru/images/icons/location-pin-icon.svg" alt="Локация" className={styles.icon} />
            <span className={styles.text}>{tournament.location}</span>
          </div>
          <div className={styles.detailItem}>
            <img src="https://app.check-checkclub.ru/images/icons/time-icon.svg" alt="Время" className={styles.icon} />
            <span className={styles.text}>{formatTournamentDate(tournament.started_at)}</span>
          </div>
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.title}>Общие правила</h2>
        <p className={styles.text}>{tournament.general_rules || 'Правила не указаны.'}</p>
      </section>

      <section className={styles.section}>
        <h2 className={styles.title}>Особенности</h2>
        {tournament.features && tournament.features.length > 0 && (
          <ul className={styles.featuresList}>
            {tournament.features.map((feature, index) => (
              <li key={index} className={styles.text}>
                {feature}
              </li>
            ))}
          </ul>
        ) || (<p className={styles.text}>Особенности не указаны</p>)}
      </section>
    </div>
  );
};

export default Info;