import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SignUp from './pages/SignUp';
import Home from './pages/Home';
import Profile from './pages/Profile';
import Tournaments from './pages/Tournaments';
import QRCode from './pages/QRCode';
import Tournament from './pages/Tournament';
import Ratings from './pages/Ratings';
import FAQ from './pages/FAQ';
import AboutClub from './pages/AboutClub';
import SocialNetworks from './pages/SocialNetworks';
import TelegramAuth from './components/TelegramAuth';
import ScrollToTop from './hooks/ScrollToTop';
import styles from './App.module.css';

function App() {
  return (
    <BrowserRouter>
      <div className={styles.App}>
        <TelegramAuth>
          <ScrollToTop />
          <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/sign_up" element={<SignUp />} />
            <Route path="/home" element={<Home />} />
            <Route path="/tournaments" element={<Tournaments />} />
            <Route path="/qr-code" element={<QRCode />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/ratings" element={<Ratings />} />
            <Route path="/tournament/:id" element={<Tournament />} />
            <Route path="/faq" element={<FAQ />} />
            <Route path="/about" element={<AboutClub />} />
            <Route path="/social-network" element={<SocialNetworks />} />
          </Routes>
        </TelegramAuth>
      </div>
    </BrowserRouter>
  );
}

export default App;
