import EllipseIcon from '@/assets/icons/ellipse.svg';
import styles from './Header.module.css';

const Header = ({ tournament }) => {
  return (
    <div className={styles.content}>
      <section className={styles.titleSection}>
        <h1 className={styles.title}>{tournament?.title || "Tournament"}</h1>
      </section>

      {
        tournament?.icon ? (
          <section className={styles.iconSection}>
            <img src={EllipseIcon} alt="Ellipse" className={styles.ellipse} />
            <img src={tournament.icon} alt="Tournament-icon" className={styles.icon} />
          </section>
        ) : null
      }

    </div>
  );
};

export default Header;