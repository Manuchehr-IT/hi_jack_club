import React from 'react';
import PaperIcon from '@/assets/icons/paper.svg'
import GameBoard from '@/assets/backgrounds/game-board.png';
import styles from '@/styles/RatingCard.module.css';

const RatingCard = () => {
  return (
    <div className={`${styles.ratingCard} ${styles.backgroundImage}`} style={{ backgroundImage: `url(${GameBoard})` }}>
      <div className={styles.cardContent}>
        <div className={styles.textContent}>
          <h2 className={styles.title}>
            РЕЙТИНГ<br />HI, JACK!
          </h2>
          <div className={styles.badge}>
            <img src={PaperIcon} alt="PaperIcon" className={styles.icon} />
            <span className={styles.badgeText}>Рейтинг игроков</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RatingCard;