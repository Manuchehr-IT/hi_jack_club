import React from 'react';
import Club from '@/assets/backgrounds/club.png';
import styles from '@/styles/AboutCard.module.css';

const AboutCard = () => {
  return (
    <div className={`${styles.aboutCard} ${styles.backgroundImage}`} style={{ backgroundImage: `url(${Club})` }}>
      <div className={styles.cardContent}>
        <div className={styles.textContent}>
          <h1 className={styles.title}>О клубе</h1>
        </div>
{/*        <div className={styles.chipImage}>
          <img src="https://app.check-checkclub.ru/images/chips/isometric/chip-logo.png" alt="Chip" />
        </div>*/}
      </div>
    </div>
  );
};

export default AboutCard;