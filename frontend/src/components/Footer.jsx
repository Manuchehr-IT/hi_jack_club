import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMe } from '@/hooks/useMe';
import HomeIcon from '@/assets/icons/home.svg';
import CardIcon from '@/assets/icons/card.svg';
import QRCodeIcon from '@/assets/icons/qr-code.svg';
import styles from '@/styles/Footer.module.css';

const Footer = () => {
  const { user } = useMe();
  const navigate = useNavigate();
  const location = useLocation();

  // Сам определяет активность по текущему URL
  const isActive = (path) => {
    return location.pathname.startsWith(path);
  };

  return (
    <div className={styles.bottomBar}>
      <nav className={styles.nav}>
        <button 
          className={`${styles.navItem} ${isActive('/home') ? styles.active : ''}`}
          onClick={() => navigate('/home')}
        >
          <div className={styles.icon}>
            <img src={HomeIcon} alt="Home" />
          </div>
        </button>

        <button 
          className={`${styles.navItem} ${isActive('/tournaments') ? styles.active : ''}`}
          onClick={() => navigate('/tournaments')}
        >
          <div className={styles.icon}>
            <img src={CardIcon} alt="Tournaments" />
          </div>
        </button>
        
        <button 
          className={`${styles.navItem} ${isActive('/qr-code') ? styles.active : ''}`}
          onClick={() => navigate('/qr-code')}
        >
          <div className={styles.icon}>
            <img src={QRCodeIcon} alt="QR-code" />
          </div>
        </button>
        
        <button 
          className={`${styles.navItem} ${isActive('/profile') ? styles.active : ''}`}
          onClick={() => navigate('/profile')}
        >
          <div className={`${styles.icon} ${styles.avatar}`}>
            {user?.avatar_path ? (
              <img src={user.avatar_path} alt="Profile" />
            ) : (
              <span style={{width: '24px', height: '24px', borderRadius: '50%', background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px'}}>👤</span>
            )}
          </div>
        </button>
      </nav>
    </div>
  );
};

export default Footer;