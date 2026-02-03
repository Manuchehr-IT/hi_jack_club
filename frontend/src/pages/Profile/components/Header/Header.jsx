import { useState } from 'react';
import EditNicknameIcon from '@/assets/icons/edit-nickname.svg';
import styles from './Header.module.css';

const Header = ({ user }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [tempNickname, setTempNickname] = useState(user?.nickname || "<Nickname>");

  const handleEditClick = () => {
    setTempNickname(user?.nickname || '');
    setIsEditing(true);
  };

  const handleSave = () => {
    if (tempNickname.trim() && onSaveNickname) {
      onSaveNickname(tempNickname.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  return (
    <section className={styles.headerSection}>
      {isEditing ? (
        <div className={styles.editContainer}>
          <input type="text" value={tempNickname} onChange={(e) => setTempNickname(e.target.value)} className={styles.nicknameInput} autoFocus/>
          <button onClick={handleCancel} className={styles.editIcon} style={{ color: "red" }} alt="Отменить">✕</button>
          <button onClick={handleSave} className={styles.editIcon} alt="Сохранить">✓</button>
        </div>
      ) : (
        <>
          <span className={styles.nickname}>{user?.nickname || "Nickname"}</span>
          <img src={EditNicknameIcon} onClick={handleEditClick} className={styles.editIcon} alt="Редактировать"/>
        </>
      )}
    </section>
  )
};

export default Header;