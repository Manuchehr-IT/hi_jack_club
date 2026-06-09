import { useState } from 'react';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton';
import { useUsers } from '@/hooks/users/useUsers';
import { useMonthlyRating } from '@/hooks/users/useMonthlyRating';
import { PageLoader } from '@/components/Loaders';
import Footer from '@/components/Footer2';
import BronzeIcon from '@/assets/icons/rating/hi_jack_bronze.svg';
import SilverIcon from '@/assets/icons/rating/hi_jack_silver_v21.svg';
import GoldIcon from '@/assets/icons/rating/hi_jack_gold.svg';
import styles from './Ratings.module.css';

const MONTHS_RU = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

const toMonthStr = (date) => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
};

const Ratings = () => {
  useTelegramBackButton(true);

  const now = new Date();
  const [tabSection, setTabSection] = useState('monthly');
  const [monthDate, setMonthDate] = useState(new Date(now.getFullYear(), now.getMonth(), 1));

  const { users: globalUsers, isLoading: globalLoading } = useUsers();
  const { users: monthlyUsers, isLoading: monthlyLoading } = useMonthlyRating(toMonthStr(monthDate));

  const isLoading = tabSection === 'global' ? globalLoading : monthlyLoading;
  const users = tabSection === 'global' ? globalUsers : monthlyUsers;

  const prevMonth = () =>
    setMonthDate(d => new Date(d.getFullYear(), d.getMonth() - 1, 1));

  const nextMonth = () => {
    const next = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 1);
    if (next <= now) setMonthDate(next);
  };

  const isCurrentMonth =
    monthDate.getFullYear() === now.getFullYear() &&
    monthDate.getMonth() === now.getMonth();

  if (globalLoading && tabSection === 'global') return <PageLoader />;

  return (
    <>
      <main className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Рейтинг Hi, Jack Club!</h1>
        </div>

        <section className={styles.tabsSection}>
          <div className={styles.buttons}>
            <button
              className={`${styles.button} ${tabSection === 'monthly' ? styles.activeTab : ''}`}
              onClick={() => setTabSection('monthly')}
            >
              <p className={styles.text}>Горячая серия месяца</p>
            </button>
            <button
              className={`${styles.button} ${tabSection === 'global' ? styles.activeTab : ''}`}
              onClick={() => setTabSection('global')}
            >
              <p className={styles.text}>Зал покерной славы</p>
            </button>
          </div>

          <div className={styles.subtitle}>
            <span>
              {tabSection === 'global'
                ? 'Фундаментальные достижения'
                : 'Насколько ты опасен прямо сейчас?'}
            </span>
          </div>
        </section>

        {tabSection === 'monthly' && (
          <div className={styles.monthPicker}>
            <button className={styles.monthArrow} onClick={prevMonth}>‹</button>
            <span className={styles.monthLabel}>
              {MONTHS_RU[monthDate.getMonth()]} {monthDate.getFullYear()}
            </span>
            <button className={styles.monthArrow} onClick={nextMonth} disabled={isCurrentMonth}>›</button>
          </div>
        )}

        <div className={styles.table}>
          <div className={`${styles.tableHeader} ${tabSection === 'monthly' ? styles.tableHeaderOrange : styles.tableHeaderGreen}`}>
            <p className={styles.headerCell}></p>
            <p className={`${styles.headerCell} ${styles.headerNicknameCell}`}>Никнеймы</p>
            <p className={styles.headerCell}>Нокауты</p>
            <p className={styles.headerCell}>Турниры</p>
            <p className={styles.headerCell}>Рейтинг</p>
          </div>

          <div className={styles.tableBody}>
            {isLoading ? (
              <div className={styles.emptyState}>Загрузка...</div>
            ) : users.length === 0 ? (
              <div className={styles.emptyState}>
                {tabSection === 'monthly' ? 'Нет данных за этот месяц' : 'Нет участников'}
              </div>
            ) : users.map((user, index) => (
              <div key={user.id} className={styles.tableRow}>
                {index + 1 <= 3
                  ? <img
                      src={{ 1: GoldIcon, 2: SilverIcon, 3: BronzeIcon }[index + 1]}
                      className={`${styles.positionCell} ${styles.numberCell}`}
                    />
                  : <p className={`${styles.positionCell} ${styles.numberCell}`}>{index + 1}</p>
                }
                <div className={`${styles.positionCell} ${styles.userCell}`}>
                  <div className={styles.userAvatar}>
                    {user?.avatar_path
                      ? <img src={user.avatar_path} alt="avatar" />
                      : <span style={{ width: '24px', height: '24px', borderRadius: '50%', background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px' }}>👤</span>
                    }
                  </div>
                  <p>{user.nickname}</p>
                </div>
                <p className={styles.positionCell}>{user.knockouts}</p>
                <p className={styles.positionCell}>{user.tournaments_count ?? 0}</p>
                <p className={styles.positionCell}>{user.rating}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
};

export default Ratings;
