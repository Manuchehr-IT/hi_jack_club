import React from 'react';
import TimeIcon from '@/assets/icons/time.svg'
import HeelIcon from '@/assets/icons/heel.svg'
import EllipseIcon from '@/assets/icons/ellipse.svg'
import styles from '@/styles/TournamentCard.module.css';
import { formatTournamentDate } from '@/utils/formatTournamentDate';

const TournamentCard = ({ tournament }) => {
  return (
    <div className={styles.tournamentCard}>
      <div className={styles.cardContent}>
        <div className={styles.textContent}>
          <h3 className={styles.title}>{tournament.title}</h3>
          <div className={styles.info}>
            {/*Кол-во Участников*/}
            {/*<div className={styles.badge}>
              <img src="https://app.check-checkclub.ru/images/icons/people-icon.svg" alt="Participants" className={styles.icon} />
              <span className={styles.badgeText}>{tournament.participants}</span>
            </div>*/}
            <div className={styles.badge}>
              <img src={TimeIcon} alt="Time" className={styles.icon} />
              <span className={styles.badgeText}>{formatTournamentDate(tournament.started_at)}</span>
            </div>
          </div>
        </div>
        <div className={styles.cardImage}>
          <img src={EllipseIcon} alt="Ellipse" className={styles.ellipse} />
          <img src={HeelIcon} alt="Tournament" className={styles.heel} />
        </div>
      </div>
    </div>
  );
};

export default TournamentCard;