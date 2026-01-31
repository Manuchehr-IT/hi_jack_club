import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useFAQ } from '@/hooks/useFAQ';
import Page from '@/components/Page';
import styles from '@/styles/FAQ.module.css';

const FAQ = () => {
  useTelegramBackButton(true);

  const { FAQ: faqItems, loading, error } = useFAQ();

  return (
    <Page loading={loading}>
      <div className={styles.header}>
        <h1 className={styles.title}>Часто задаваемые вопросы</h1>
      </div>

      <div className={styles.content}>
        {faqItems.map((item, index) => (
          <div className={styles.faqItem} key={item.id}>
            <h3 className={styles.question}>
              <span className={styles.number}>{index + 1}.</span>
              {item.question}
            </h3>
            <div className={styles.answer}>{item.answer}</div>
          </div>
        ))}
      </div>
    </Page>
  );
};

export default FAQ;
