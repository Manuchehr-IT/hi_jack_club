import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useAboutClub } from '@/hooks/useAboutClub';
import { PageLoader } from '@/components/Loaders';
import Page from '@/components/Page';
import InfiniteCarousel from '@/components/InfiniteCarousel';
import styles from '@/styles/AboutClub.module.css';
import { hasText } from '@/utils/htmlHelpers';

const AboutClub = () => {
  useTelegramBackButton(true);

  const { aboutClub: blocks, loading } = useAboutClub();

  return (
    <Page loading={loading}>
      <div className={styles.header}>
        <h1 className={styles.title}>О нашем клубе</h1>
      </div>

      <div className={styles.content}>
        <div className={styles.section}>
          {blocks.map((block) => (
            <div key={block.id} className={styles.block}>
              {hasText(block.text) && (
                <div className={styles.text} dangerouslySetInnerHTML={{ __html: block.text }} />
              )}
              {block.images && block.images.length > 0 && (
                <InfiniteCarousel images={block.images} />
              )}
            </div>
          ))}
        </div>
      </div>
    </Page>
  );
};

export default AboutClub;