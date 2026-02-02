import { useTelegramBackButton } from '@/hooks/telegram/useTelegramBackButton'
import { useSocialNetworks } from '@/hooks/useSocialNetworks';
import { PageLoader } from '@/components/Loaders';
import Footer from '@/components/Footer2';
import Header from './components/Header';
import Content from './components/Content';

const SocialNetworks = () => {
  useTelegramBackButton(true);

  const { socialNetworks, isLoading, error } = useSocialNetworks();

  if (isLoading) return <PageLoader />;

  return (
    <>
      <Header/>
      <Content socialNetworks={socialNetworks}/>
      <Footer/>
    </>
  );
};

export default SocialNetworks;