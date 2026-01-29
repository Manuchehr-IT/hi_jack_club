import React from 'react';
import GPSIcon from '@/assets/icons/gps.svg';
import TGIcon from '@/assets/icons/tg.svg';
import VKIcon from '@/assets/icons/vk.svg';
import IGIcon from '@/assets/icons/ig.svg';
import BroadcastIcon from '@/assets/icons/broadcast.svg';
import styles from '@/styles/social-network/Buttons.module.css';

const Buttons = ({ socialNetwork }) => {
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
    <div className={styles.container}>
      <button className={`${styles.button} ${styles.map}`} onClick={() => openLink(socialNetwork.map)}>
        <img src={GPSIcon} alt="gps-icon" className={styles.icon} />
        <p className={styles.text}>Построить маршрут</p>
      </button>
      <button className={`${styles.button} ${styles.tg}`} onClick={() => openLink(socialNetwork.tg, true)}>
        <img src={TGIcon} alt="telegram-icon" className={styles.icon} />
        <p className={styles.text}>Telegram-канал</p>
      </button>
      <button className={`${styles.button} ${styles.vk}`} onClick={() => openLink(socialNetwork.vk)}>
        <img src={VKIcon} alt="vk-icon" className={styles.icon} />
        <p className={styles.text}>ВКонтакте</p>
      </button>
      <button className={`${styles.button} ${styles.ig}`} onClick={() => openLink(socialNetwork.ig)}>
        <img src={IGIcon} alt="ig-icon" className={styles.icon} />
        <p className={styles.text}>Instagram</p>
      </button>
      <button className={`${styles.button} ${styles.broadcast}`} onClick={() => openLink(socialNetwork.vk_broadcast)}>
        <img src={BroadcastIcon} alt="broadcast-icon" className={styles.icon} />
        <p className={styles.text}>VK Видео (Эфир)</p>
      </button>
      <button className={`${styles.button} ${styles.broadcast}`} onClick={() => openLink(socialNetwork.vk_broadcast_archive)}>
        <img src={BroadcastIcon} alt="broadcast-icon" className={styles.icon} />
        <p className={styles.text}>VK Видео (Архив трансляций)</p>
      </button>
    </div>
  );
};

export default Buttons;
