import SocialNetworkHeaderIcon from '@/assets/icons/social-network-header.svg';
import styles from '@/styles/social-network/Header.module.css';

const Header = () => {
  return (
    <div className={styles.container}>
      <div className={styles.text}>
        <h1 className={styles.title}>Мы в соцсетях</h1>
      </div>

      <div className={styles.icon}>
        <img src={SocialNetworkHeaderIcon} alt="Social Network icon" className={styles.socialNetworkIcon} />
      </div>
    </div>
  )
};

export default Header;
