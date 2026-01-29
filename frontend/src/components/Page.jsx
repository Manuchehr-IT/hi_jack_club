import { PageLoader } from './Loaders';
import Footer from './Footer';
import styles from '@/styles/Page.module.css'

const Page = ({ children, loading = false, showFooter = true }) => {
  if (loading) {
    return <PageLoader />;
  }

  return (
    <>
      <main className={styles.outlet}>
        {children}
      </main>

      {showFooter && (
        <footer className={styles.footer}>
          <Footer />
        </footer>
      )}
    </>
  );
};

export default Page;
