import { useSocialNetwork } from '@/hooks/useSocialNetwork';
import Page from '@/components/Page';
import Header from '@/components/social-network/Header';
import Buttons from '@/components/social-network/Buttons';
import Info from '@/components/social-network/Info';

const SocialNetwork = () => {
  const { socialNetwork, loading, error } = useSocialNetwork();

  // TODO page

  return (
    <Page loading={loading}>
      <Header />
      <Buttons socialNetwork={socialNetwork} />
      <Info />
    </Page>
  );
};

export default SocialNetwork;