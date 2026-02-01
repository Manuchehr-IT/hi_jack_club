import { useMe } from '@/hooks/useMe';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import Page from '@/components/Page';
import styles from '@/styles/Profile.module.css';

const Profile = () => {
  useTelegramBackButton(false);

  const { user, loading, error } = useMe();

  return (
    <Page loading={loading}>
      <div className={styles.header}>
        <span className={styles.nickname}>{user?.nickname || "Nickname"}</span>
        <img src="https://app.check-checkclub.ru/images/icons/profile-info-icon.svg" />
      </div>

      <div className={styles.content}>
        <p>Информация о профиле...</p>
      </div>
    </Page>
  );
};

export default Profile;