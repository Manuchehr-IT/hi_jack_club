import { useState } from 'react';
import { IoMdSettings } from 'react-icons/io';
import { GoCheck, GoX } from 'react-icons/go';
import { RotatingLines } from 'react-loader-spinner';
import { useMe } from '@/hooks/useMe';
import EditNicknameIcon from '@/assets/icons/edit-nickname.svg';
import styles from './Header.module.css';

const Header = ({ user, isLoading, updateProfile }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [tempNickname, setTempNickname] = useState(user?.nickname || "");

  console.log("isLoading:", isLoading)

  const handleEditClick = () => {
    setTempNickname(user?.nickname || "");
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const handleSave = async () => {
    await updateProfile({nickname: tempNickname.trim()});
    setIsEditing(false);
  };

  return (
    <section className={styles.headerSection}>
      {isEditing ? (
        <div className={styles.editContainer}>
          <input type="text" value={tempNickname} onChange={(e) => setTempNickname(e.target.value)} className={styles.nicknameInput} autoFocus/>

          <button onClick={handleCancel} disabled={isLoading} alt="Отменить"><GoX className={styles.cancelIcon}/></button>
          <button onClick={handleSave} disabled={isLoading | !user?.nickname} alt="Сохранить">
            {isLoading ? <RotatingLines color="white" height="24"/> : <GoCheck className={styles.confirmIcon}/>}
          </button>
        </div>
      ) : (
        <>
          <span className={styles.nickname}>{user?.nickname || "Nickname"}</span>
          <IoMdSettings className={styles.editNicknameIcon} onClick={handleEditClick}/>
        </>
      )}
    </section>
  )
};

export default Header;