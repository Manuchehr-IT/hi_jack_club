// src/components/icons/PokerIcons.jsx
import React from 'react';
import { 
  FaTrophy, 
  FaQuestionCircle, 
  FaHeadset, 
  FaHome,
  FaUser
} from 'react-icons/fa';
import { GiPokerHand } from 'react-icons/gi';

export const TrophyIcon = () => (
  <FaTrophy className="icon-trophy" size={20} />
);

export const HelpIcon = () => (
  <FaQuestionCircle className="icon-help" size={20} />
);

export const SupportIcon = () => (
  <FaHeadset className="icon-support" size={20} />
);

export const ClubIcon = () => (
  <GiPokerHand className="icon-club" size={20} />
);

export const HomeIcon = ({ active }) => (
  <FaHome className={active ? "icon-home active" : "icon-home"} size={20} />
);

// ИСПРАВЛЕНО: Теперь это кубок для турниров
export const TournamentIcon = ({ active }) => (
  <FaTrophy className={active ? "icon-tournament active" : "icon-tournament"} size={18} />
);

export const ProfileIcon = ({ active }) => (
  <FaUser className={active ? "icon-profile active" : "icon-profile"} size={18} />
);