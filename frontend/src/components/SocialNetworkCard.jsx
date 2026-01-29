import React from 'react';
import SocialNetworkIcon from '@/assets/icons/social-network.svg'
import styles from '@/styles/SocialNetworkCard.module.css';

const SocialNetworkCard = () => {
  return (
    <div className={styles.card}>
      <div className={styles.content}>
        <div className={styles.text}>
          <h3 className={styles.title}>Мы в соцсетях</h3>
        </div>
        <div className={styles.image}>
          <img src={SocialNetworkIcon} alt="social-network" className={styles.socialNetworkIcon} />
        </div>
      </div>
    </div>
  );
};

export default SocialNetworkCard;