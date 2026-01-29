// src/components/icons/CustomIcons.jsx
import React from 'react';

export const TrophyIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M8 21H16M12 17V21M17 5V3H7V5M5 7V12C5 15.866 8.134 17 12 17C15.866 17 19 15.866 19 12V7H5Z" 
          stroke="#FFD700" strokeWidth="2" strokeLinecap="round"/>
    <path d="M12 17C15.866 17 19 15.866 19 12V7H5V12C5 15.866 8.134 17 12 17Z" 
          fill="#FFD700" fillOpacity="0.2"/>
  </svg>
);

export const HelpIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="9" stroke="#6C5CE7" strokeWidth="2"/>
    <circle cx="12" cy="18" r="0.5" fill="#6C5CE7"/>
    <path d="M12 16V14C13.1046 14 14 13.1046 14 12C14 10.8954 13.1046 10 12 10C10.8954 10 10 10.8954 10 12" 
          stroke="#6C5CE7" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

export const SupportIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M8 10H8.01M12 10H12.01M16 10H16.01M6 16H18C19.1046 16 20 15.1046 20 14V6C20 4.89543 19.1046 4 18 4H6C4.89543 4 4 4.89543 4 6V14C4 15.1046 4.89543 16 6 16Z" 
          stroke="#E84393" strokeWidth="2" strokeLinecap="round"/>
    <path d="M8 10C8 10.5523 7.55228 11 7 11C6.44772 11 6 10.5523 6 10C6 9.44772 6.44772 9 7 9C7.55228 9 8 9.44772 8 10Z" fill="#E84393"/>
    <path d="M12 10C12 10.5523 11.5523 11 11 11C10.4477 11 10 10.5523 10 10C10 9.44772 10.4477 9 11 9C11.5523 9 12 9.44772 12 10Z" fill="#E84393"/>
    <path d="M16 10C16 10.5523 15.5523 11 15 11C14.4477 11 14 10.5523 14 10C14 9.44772 14.4477 9 15 9C15.5523 9 16 9.44772 16 10Z" fill="#E84393"/>
  </svg>
);

export const ClubIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M12 3C12 3 7 7 7 11C7 14.866 9.134 16 12 16C14.866 16 17 14.866 17 11C17 7 12 3 12 3Z" 
          stroke="#00B894" strokeWidth="2"/>
    <path d="M12 16V21" stroke="#00B894" strokeWidth="2" strokeLinecap="round"/>
    <path d="M9 19H15" stroke="#00B894" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

export const HomeIcon = ({ active }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M3 9L12 2L21 9V20C21 20.5523 20.5523 21 20 21H4C3.44772 21 3 20.5523 3 20V9Z" 
          stroke={active ? "#FF4444" : "#888"} strokeWidth="2"/>
    <path d="M9 21V12H15V21" 
          stroke={active ? "#FF4444" : "#888"} strokeWidth="2" strokeLinecap="round"/>
    {active && <path d="M3 9L12 2L21 9" stroke="#FF4444" strokeWidth="2" strokeLinecap="round"/>}
  </svg>
);

export const TournamentIcon = ({ active }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M8 7V3H16V7M8 7H6C4.89543 7 4 7.89543 4 9V19C4 20.1046 4.89543 21 6 21H18C19.1046 21 20 20.1046 20 19V9C20 7.89543 19.1046 7 18 7H16M8 7H16" 
          stroke={active ? "#00B894" : "#888"} strokeWidth="2" strokeLinecap="round"/>
    <path d="M12 12V16M10 14H14" 
          stroke={active ? "#00B894" : "#888"} strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

export const ProfileIcon = ({ active }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="8" r="4" stroke={active ? "#6C5CE7" : "#888"} strokeWidth="2"/>
    <path d="M5 20C5 16.134 8.13401 14 12 14C15.866 14 19 16.134 19 20" 
          stroke={active ? "#6C5CE7" : "#888"} strokeWidth="2" strokeLinecap="round"/>
  </svg>
);