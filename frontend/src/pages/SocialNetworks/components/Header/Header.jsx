import SocialNetworkHeaderIcon from '@/assets/icons/social-network-header.svg';
import styles from './Header.module.css';

const Header = () => {
  return (
    <div className={styles.content}>
      <section className={styles.titleSection}>
        <h1 className={styles.title}>Мы в соцсетях</h1>
      </section>

      <section className={styles.iconSection}>
        <img src={SocialNetworkHeaderIcon} alt="Social Network icon" className={styles.icon} />
      </section>
    </div>
  )
};

export default Header;
