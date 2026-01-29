import React from 'react';
import styles from '@/styles/social-network/Info.module.css';

const Info = () => {
  const contentText = '* Компания Meta Platforms Inc., владеющая социальной сетью Instagram, по решению суда от 21.03.2022 признана экстремистской организацией, ее деятельность на территории России запрещена'

  return (
    <div className={styles.container}>
      <p className={styles.text}>{contentText}</p>
    </div>
  );
};

export default Info;