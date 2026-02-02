import React from 'react';
import TimeIcon from '@/assets/icons/time.svg'
import EllipseIcon from '@/assets/icons/ellipse.svg'
import styles from '@/styles/TournamentCard.module.css';
import { formatTournamentDate } from '@/utils/formatTournamentDate';

const TournamentCard = ({ tournament }) => {
  const imageIcon = tournament?.icon
  ? (
    <div className={styles.cardImages}>
      <img src={EllipseIcon} alt="Ellipse" className={styles.ellipse} />
      <img src={tournament.icon} alt="Tournament-icon" className={styles.imageIcon} />
    </div>
  )
  : null;

  return (
    <div className={styles.tournamentCard}>
      <div className={styles.cardContent}>

        <div className={styles.textContent}>
          <h3 className={styles.title}>{tournament.title}</h3>
          <div className={styles.info}>
            <div className={styles.badge}>
              <img src={TimeIcon} alt="Time" className={styles.icon} />
              <span className={styles.badgeText}>{formatTournamentDate(tournament.started_at)}</span>
            </div>
          </div>
        </div>

        {imageIcon}

      </div>
    </div>
  );
};

export default TournamentCard;