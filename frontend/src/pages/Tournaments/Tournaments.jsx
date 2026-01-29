import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTournaments } from '@/hooks/useTournaments';
import Page from '@/components/Page';
import TournamentCard from '@/components/TournamentCard';
import styles from './Tournaments.module.css';

const Tournaments = () => {
  const { tournaments, loading, error } = useTournaments();
  const navigate = useNavigate();

  // console.log(error)

  // if (!loading && error) {
  //   return 1; // TODO page
  // }

  // if (!loading && (!tournaments || tournaments.length === 0)) {
  //   return 2; // TODO page
  // }

  return (
    <Page loading={loading}>
      <div className={styles.content}>
        {tournaments.map((tournament) => (
          <div key={tournament.id} onClick={() => navigate(`/tournament/${tournament.id}`)}>
            <TournamentCard tournament={tournament} />
          </div>
        ))}
      </div>
    </Page>
  );
};

export default Tournaments;
