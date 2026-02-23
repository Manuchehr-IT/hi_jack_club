import { useState, useEffect } from 'react';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useUsers } from '@/hooks/users/useUsers';
import { PageLoader } from '@/components/Loaders';
import Footer from '@/components/Footer2';
import BronzeIcon from '@/assets/icons/rating/hi_jack_bronze.svg'
import SilverIcon from '@/assets/icons/rating/hi_jack_silver_v21.svg'
import GoldIcon from '@/assets/icons/rating/hi_jack_gold.svg'
import HiJackGlobal from '@/assets/icons/rating/Poker_Hall_of_Fame.svg'
import HiJackMonthly from '@/assets/icons/rating/Hot_Series_Month.svg'
import styles from './Ratings.module.css';

const Ratings = () => {
  useTelegramBackButton(true);

  const { users, isLoading, error } = useUsers();

  const [tabSection, setTabSection] = useState("global");

  if (isLoading) return <PageLoader/>;

  return (
    <>
      <main className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Рейтинг Hi, Jack Club!</h1>
        </div>

        <section className={styles.tabsSection}>
          <div className={styles.buttons}>
            <button className={styles.button}>
              {/*<img src={HiJackMonthly} alt="" height="40px"/>*/}
              <p className={styles.text}>Горячая серия месяца</p>
            </button>
            <button className={styles.button}>
              {/*<img src="" alt=""/>*/}
              <p className={styles.text}>Зал покерной славы</p>
            </button>
          </div>
          <div className={styles.subtitle}>
            <span>{tabSection == "global" ? "Фундаментальные достижения" : "Насколько ты опасен прямо сейчас?"}</span>
          </div>
        </section>

        {/* Таблица рейтингов */}
        <div className={styles.table}>
          {/* Заголовки таблицы */}
          <div className={styles.tableHeader}>
            <p className={styles.headerCell}></p>
            <p className={`${styles.headerCell} ${styles.headerNicknameCell}`}>Никнеймы</p>
            <p className={styles.headerCell}>Нокауты</p>
            <p className={styles.headerCell}>Турниры</p>
            <p className={styles.headerCell}>Рейтинг</p>
          </div>

          {/* Строки таблицы */}
          <div className={styles.tableBody}>
            {users.map((user, index) => (
              <div key={user.id} className={styles.tableRow}>
                {
                  index + 1 <= 3
                    ? <img src={{1:GoldIcon, 2:SilverIcon, 3:BronzeIcon}[index + 1]} className={`${styles.positionCell} ${styles.numberCell}`}/>
                    : <p className={`${styles.positionCell} ${styles.numberCell}`}>{index +1}</p>
                }
                <div className={`${styles.positionCell} ${styles.userCell}`}>
                  <div className={styles.userAvatar}>
                    {user?.avatar_path
                      ? <img src={user.avatar_path} alt="avatar"/>
                      : <span style={{width: '24px', height: '24px', borderRadius: '50%', background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px'}}>👤</span>
                    }
                  </div>
                  <p>{user.nickname}</p>
                </div>
                <p className={`${styles.positionCell}`}>{user.knockouts}</p>
                <p className={`${styles.positionCell}`}>Null</p>
                <p className={`${styles.positionCell}`}>{user.rating}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
      <Footer/>
    </>
  );
};

export default Ratings;
