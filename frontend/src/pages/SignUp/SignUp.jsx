import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useSignUp } from "@/hooks/useSignUp";
import { useMe } from "@/hooks/useMe";
import { PageLoader } from '@/components/Loaders';
import styles from './SignUp.module.css';

const SignUp = () => {
  useTelegramBackButton(false);

  const { user, loading: userLoading, error: userError, refetch: userFetch } = useMe();
  const { loading: signUpLoading, error: signUpError, signUp } = useSignUp();
  const [countryCode, setCountryCode] = useState("+7");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [nickname, setNickname] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!signUpLoading && user?.privacy_policy_accepted) {
      console.log("Навигация на /home [SignUp]");
      navigate("/home");
    }
  }, [user, signUpLoading, navigate]);

  if (userLoading) return <PageLoader/>;

  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(/\D/g, '');
    setPhoneNumber(value);
  };

  const handleNicknameChange = (e) => {
    setNickname(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!nickname.trim() || !phoneNumber) return;

    setIsSubmitting(true);
    try {
      const result = await signUp({
        nickname,
        phone_code: countryCode,
        phone: phoneNumber,
        privacy_policy_accepted: true,
      });
      console.log("Регистрация успешна:", result);
      navigate("/home");
    } catch (error) {
      console.error("Ошибка регистрации:", error);
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormValid = nickname.trim().length >= 3 && phoneNumber.length >= 10;

  return (
    <main className={styles.content}>
      <header className={styles.header}>
        <h1 className={styles.title}>Регистрация</h1>
        <p className={styles.subtitle}>Создайте аккаунт для доступа к сервису</p>
      </header>

      <form onSubmit={handleSubmit} className={styles.form}>
        <section className={styles.section}>
          <label htmlFor="nickname" className={styles.label}>Никнейм</label>
          <div className={styles.inputGroup}>
            <input
              id="nickname"
              type="text"
              className={styles.input}
              value={nickname}
              onChange={handleNicknameChange}
              placeholder="Введите ваш никнейм"
              maxLength={30}
              required
              autoComplete="username"
              disabled={isSubmitting}
            />
          </div>
        </section>

        <section className={styles.section}>
          <label htmlFor="phone" className={styles.label}>Номер телефона</label>
          <div className={styles.phoneInput}>
            <select 
              id="countryCode"
              className={styles.countryCode}
              value={countryCode}
              onChange={(e) => setCountryCode(e.target.value)}
              disabled={isSubmitting}
            >
              <option value="+7">🇷🇺 +7</option>
            </select>
            <input
              id="phone"
              type="tel"
              inputMode="numeric"
              className={styles.input}
              value={phoneNumber}
              onChange={handlePhoneChange}
              placeholder="999 123 45 67"
              maxLength={10}
              required
              autoComplete="tel"
              disabled={isSubmitting}
            />
          </div>
        </section>

        <div className={styles.privacy}>
          <a 
            href={import.meta.env.VITE_PRIVACY_POLICY} 
            target="_blank" 
            rel="noopener noreferrer"
            className={styles.privacyLink}
          >
            Политика конфиденциальности
          </a>
          <p className={styles.privacyText}>
            Нажимая "Подтвердить", вы соглашаетесь с нашей политикой конфиденциальности
          </p>
        </div>

        <div>
          <button type="submit" className={styles.submitButton} disabled={!isFormValid || isSubmitting}>
            {isSubmitting ? (<span className={styles.loadingText}>Обработка...</span>) : ("Подтвердить")}
          </button>
          {signUpError && <p className={styles.hintText}>{signUpError}</p>}
        </div>
      </form>
    </main>
  );
};

export default SignUp;