import { useState } from 'react';
import { useMe } from '@/hooks/useMe';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { ContentLoader } from '@/components/Loaders'
import Page from '@/components/Page';
import ReferralIcon from '@/assets/icons/referral.jpg';
import styles from './Profile.module.css';

const Profile = () => {
  useTelegramBackButton(false);
  const { user, loading, error } = useMe();
  const [copied, setCopied] = useState(false);

  const telegramBotUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME

  const referralLink = (user?.referral_code && telegramBotUsername) ? `https://t.me/${telegramBotUsername}/app?startapp=${user.referral_code}` : "";
  const referralLinkContent = referralLink || <ContentLoader />

  const handleCopyLink = async () => {
    if (!referralLink) return;

    try {
      await navigator.clipboard.writeText(referralLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const handleShare = async () => {
    if (!referralLink) return;

    const tg = window.Telegram?.WebApp;

    if (tg && tg.shareToChat) {
      tg.shareToChat(referralLink, "Присоединяйся к нам");
    } else {
      handleShareFallback();
    }
  };

  const handleShareFallback = () => {
    if (navigator.share) {
      navigator.share({
        title: "Присоединяйся!",
        text: "Присоединяйся к нашему сообществу",
        url: referralLink,
      }).catch(console.error);
    } else {
      handleCopyLink();
    }
  };


  return (
    <Page loading={loading}>

      <div className={styles.container}>
        <div className={styles.header}>
          <span className={styles.nickname}>{user?.nickname || "Nickname"}</span>
          <img src="https://app.check-checkclub.ru/images/icons/profile-info-icon.svg" />
        </div>

        {/* Статистика профиля */}
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <div className={styles.statInfo}>
              <span className={styles.statNumber}>
                {user?.referrals?.length || 0}
              </span>
              <span className={styles.statLabel}>Рефералов</span>
            </div>
          </div>
        </div>

        {/* Реферальная ссылка */}
        <div className={styles.referralSection}>
          <h3 className={styles.sectionTitle}>
            {/*<LinkIcon />*/}
            Пригласи друга
          </h3>
          <p className={styles.sectionDescription}>
            Делитесь ссылкой и получайте бонусы за каждого приглашенного друга
          </p>
          
          <div className={styles.referralLinkContainer}>
            <div className={styles.referralLink}>
              <span className={styles.linkText}>
                {referralLinkContent}
              </span>
            </div>
            
            <div className={styles.linkActions}>
              <button 
                className={`${styles.actionButton} ${copied ? styles.copied : ""}`}
                onClick={handleCopyLink}
                disabled={!referralLink}
              >
                {/*<CopyIcon />*/}
                <span className={styles.actionText}>{copied ? "Скопировано!" : "Копировать"}</span>
              </button>
              
              <button 
                className={styles.actionButton}
                onClick={handleShare}
                disabled={!referralLink}
              >
                {/*<ShareIcon />*/}
                <span className={styles.actionText}>Поделиться</span>
              </button>
            </div>
          </div>
        </div>

      </div>
    </Page>
  );
};

export default Profile;