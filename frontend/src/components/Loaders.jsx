import { BeatLoader, FadeLoader, SkewLoader, SyncLoader } from 'react-spinners';
import styles from '@/styles/Loaders.module.css'

export const PageLoader = () => (
  <div className={styles.pageLoader}>
    <SyncLoader color="white" />
  </div>
);

export const AuthLoader = () => (
  <div className={styles.pageLoader}>
    <FadeLoader color="white" />
  </div>
);

export const ContentLoader = () => (
  <div className={styles.contentLoader}>
    <BeatLoader color="black"/>
  </div>
);
