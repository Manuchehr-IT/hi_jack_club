import { useState } from 'react';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useMe } from '@/hooks/useMe';
import { ContentLoader } from '@/components/Loaders'
import { PageLoader } from '@/components/Loaders';
import Footer from '@/components/Footer2';
import Header from './components/Header';
import HiJackIcon from '@/assets/icons/social-network.svg';
import styles from './Profile.module.css';

const Profile = () => {
  useTelegramBackButton(false);

  const { user, loading, isLoading, error, updateProfile } = useMe();
  const [copied, setCopied] = useState(false);

  if (loading) return <PageLoader />;

  const telegramBotUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME

  const referralLink = (user?.referral_code && telegramBotUsername) ? `https://t.me/${telegramBotUsername}/app?startapp=${user.referral_code}` : "";
  const referralLinkContent = referralLink || <ContentLoader />

  const handleCopyLink = async () => {
    if (!referralLink) return;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(referralLink);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        return;
      } catch (err) {
        console.warn("Clipboard API failed, trying fallback:", err);
      }
    } else {
      fallbackCopy();
    }
  };

  // Запасной метод для старых браузеров и Android
  const fallbackCopy = () => {
    try {
      // Создаем временный textarea элемент
      const textarea = document.createElement('textarea');
      textarea.value = referralLink;

      // Делаем элемент невидимым
      textarea.style.position = 'fixed';
      textarea.style.top = '-9999px';
      textarea.style.left = '-9999px';
      textarea.style.opacity = '0';

      document.body.appendChild(textarea);

      // Выделяем текст и копируем
      textarea.focus();
      textarea.select();
      textarea.setSelectionRange(0, 99999); // Для мобильных устройств

      const successful = document.execCommand('copy');

      // Удаляем временный элемент
      document.body.removeChild(textarea);

      if (successful) {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } else {
        console.error("Fallback copy failed");
        // Здесь можно показать пользователю сообщение с просьбой скопировать вручную
      }
    } catch (err) {
      console.error("Fallback copy error:", err);
    }
  };

  const handleShare = () => {
    if (!referralLink) return;

    const fullText = "\nHi, Jack — игра начинается с тебя!\nХод за тобой — переходи по ссылке.";

    const shareUrl =
      `https://t.me/share/url?` +
      `url=${encodeURIComponent(referralLink)}` +
      `&text=${encodeURIComponent(fullText)}`;

    if (window.Telegram?.WebApp?.openTelegramLink) {
      console.log(window.Telegram.WebApp)
      window.Telegram.WebApp.openTelegramLink(shareUrl);
    } else {
      // если открыли вне Telegram
      window.open(shareUrl, "_blank");
    }
  };



  return (
    <>
      <main className="container">

        <Header user={user} isLoading={isLoading} updateProfile={updateProfile}/>

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
          <p className={styles.sectionDescription}>Делитесь ссылкой и получайте Hi Donats за каждого приглашенного друга</p>
          
          <div className={styles.referralLinkContainer}>
            {/*<div className={styles.referralLink}>
              <span className={styles.linkText}>
                {referralLinkContent}
              </span>
            </div>*/}

            <div className={styles.linkActions}>
              <button 
                className={`${styles.actionButton} ${copied ? styles.copied : ""}`}
                onClick={handleCopyLink}
                disabled={!referralLink || copied}
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
          <dev className={styles.bgIcon}>
            <img src={HiJackIcon} className={styles.hiJackIcon}/>
          </dev>
        </div>
      </main>
      <Footer/>
    </>
  );
};

export default Profile;