import React from 'react';
import styles from '@/styles/GridCard.module.css';

const GridCard = ({ title, className, onClick }) => {
  return (
    <div className={`${styles.gridCard} ${className}`} onClick={onClick}>
      <div className={styles.cardContent}>
        <h2 className={styles.title}>{title}</h2>
      </div>
    </div>
  );
};

export default GridCard;