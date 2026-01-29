import React from 'react';
import Footer from './Footer';

const Layout = ({ children }) => {
  return (
    <div className="layout">
      <div className="App">
        <main className="layout-content">
          {children}
        </main>
      </div>

      <footer className="layout-footer">
        <Footer />
      </footer>
    </div>
  );
};

export default Layout;