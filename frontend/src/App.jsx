import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import CurationDashboard from './components/CurationDashboard';
import Dashboard from './components/Dashboard';
import ConfigurationManager from './components/ConfigurationManager';
import VictorChat from './components/VictorChat';
import { isAuthenticated } from './auth';

function App() {
  const [isAuth, setIsAuth] = useState(isAuthenticated());
  const [view, setView] = useState('dashboard'); // 'dashboard' | 'curation' | 'config' | 'victor_chat'

  const handleLoginSuccess = () => {
    setIsAuth(true);
  };

  const handleLogout = () => {
    setIsAuth(false);
    setView('dashboard');
  };

  return (
    <div className="App">
      {!isAuth ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : view === 'curation' ? (
        <CurationDashboard onBack={() => setView('dashboard')} />
      ) : view === 'config' ? (
        <ConfigurationManager onBack={() => setView('dashboard')} />
      ) : (
        <>
          <Dashboard
            onLogout={handleLogout}
            onNavigateCuration={() => setView('curation')}
            onNavigateConfig={() => setView('config')}
            onNavigateVictorChat={() => setView('victor_chat')}
          />
          <VictorChat
            show={view === 'victor_chat'}
            onHide={() => setView('dashboard')}
          />
        </>
      )}
    </div>
  );
}

export default App;
