import React from 'react';
import GPSIcon from '@/assets/icons/gps.svg';
import TGIcon from '@/assets/icons/tg.svg';
import VKIcon from '@/assets/icons/vk.svg';
import IGIcon from '@/assets/icons/ig.svg';
import BroadcastIcon from '@/assets/icons/broadcast.svg';
import styles from './Content.module.css';

const Content = ({ socialNetworks }) => {
  const openLink = (url, inTelegram = false) => {
    if (!url || url.trim() === "") {
      Telegram.WebApp.showAlert("Ссылка не указана");
      return;
    }

    if (inTelegram) {
      Telegram.WebApp.openTelegramLink(url);
    } else {
      Telegram.WebApp.openLink(url);
    }
  };

  return (
    <main className="container">
      <section className={styles.socialNetworksSection}>
        <button className={`${styles.button} ${styles.map}`} onClick={() => openLink(socialNetworks.map)}>
          <img src={GPSIcon} alt="gps-icon" className={styles.icon} />
          <p className={styles.text}>Построить маршрут</p>
        </button>
        <button className={`${styles.button} ${styles.tg}`} onClick={() => openLink(socialNetworks.tg, true)}>
          <img src={TGIcon} alt="telegram-icon" className={styles.icon} />
          <p className={styles.text}>Telegram-канал</p>
        </button>
        <button className={`${styles.button} ${styles.vk}`} onClick={() => openLink(socialNetworks.vk)}>
          <img src={VKIcon} alt="vk-icon" className={styles.icon} />
          <p className={styles.text}>ВКонтакте</p>
        </button>
        <button className={`${styles.button} ${styles.ig}`} onClick={() => openLink(socialNetworks.ig)}>
          <img src={IGIcon} alt="ig-icon" className={styles.icon} />
          <p className={styles.text}>Instagram</p>
        </button>
        <button className={`${styles.button} ${styles.broadcast}`} onClick={() => openLink(socialNetworks.vk_broadcast)}>
          <img src={BroadcastIcon} alt="broadcast-icon" className={styles.icon} />
          <p className={styles.text}>VK Видео (Эфир)</p>
        </button>
        <button className={`${styles.button} ${styles.broadcast}`} onClick={() => openLink(socialNetworks.vk_broadcast_archive)}>
          <img src={BroadcastIcon} alt="broadcast-icon" className={styles.icon} />
          <p className={styles.text}>VK Видео (Архив трансляций)</p>
        </button>
      </section>

      <section className={styles.footerSection}>
        <p className={styles.text}>
          * Компания Meta Platforms Inc., владеющая социальной сетью Instagram, по решению суда от 21.03.2022 признана экстремистской организацией,
          ее деятельность на территории России запрещена
        </p>
      </section>
    </main>
  );
};

export default Content;
