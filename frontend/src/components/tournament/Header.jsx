import HeelIcon from '@/assets/icons/heel.svg';
import EllipseIcon from '@/assets/icons/ellipse.svg';
import styles from '@/styles/tournament/Header.module.css';

const Header = ({ tournament }) => {
  return (
    <div className={styles.container}>
      <div className={styles.textSection}>
        <h1 className={styles.title}>{tournament?.title || "Tournament"}</h1>
      </div>

      <div className={styles.iconSection}>
        <img src={EllipseIcon} alt="Ellipse" className={styles.ellipse} />
        <img src={HeelIcon} alt="Tournament icon" className={styles.icon} />
      </div>
    </div>
  );
};

export default Header;