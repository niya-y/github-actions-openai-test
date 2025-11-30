import { useState } from 'react';
import './App.css';
import Welcome from './pages/Welcome';
import PersonalityTest from './pages/PersonalityTest';
import Recommendations from './pages/Recommendations';
import Dashboard from './pages/Dashboard';

function App() {
  const [currentPage, setCurrentPage] = useState('welcome');
  const [menuOpen, setMenuOpen] = useState(false);

  const navigateTo = (page) => {
    setCurrentPage(page);
    setMenuOpen(false);
  };

  return (
    <div className="flex justify-center items-start min-h-screen bg-gray-100 dark:bg-gray-900 font-display">
      {/* Mobile Phone Container */}
      <div className="relative w-full max-w-lg mx-auto flex flex-col group/design-root overflow-x-hidden bg-background-light dark:bg-background-dark min-h-screen">

        {/* Top Header with Logo and Hamburger Menu - All Pages */}
        <header className="sticky top-0 z-40 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <span className="material-symbols-outlined text-primary text-2xl">health_and_safety</span>
              <span className="font-bold tracking-tight text-text-primary-light dark:text-text-primary-dark">바른케어</span>
            </div>

            {/* Hamburger Menu Button */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="flex items-center justify-center text-text-primary-light dark:text-text-primary-dark hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded"
            >
              <span className="material-symbols-outlined text-2xl">menu</span>
            </button>
          </div>

          {/* Dropdown Menu */}
          {menuOpen && (
            <nav className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-2 space-y-1 mt-3 border border-gray-200 dark:border-gray-700">
              <button
                onClick={() => navigateTo('welcome')}
                className={`w-full text-left px-4 py-2 rounded flex items-center space-x-2 transition ${
                  currentPage === 'welcome'
                    ? 'bg-blue-50 dark:bg-blue-900 text-primary'
                    : 'text-text-primary-light dark:text-text-primary-dark hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <span className="material-symbols-outlined">home</span>
                <span>홈</span>
              </button>
              <button
                onClick={() => navigateTo('test')}
                className={`w-full text-left px-4 py-2 rounded flex items-center space-x-2 transition ${
                  currentPage === 'test'
                    ? 'bg-blue-50 dark:bg-blue-900 text-primary'
                    : 'text-text-primary-light dark:text-text-primary-dark hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <span className="material-symbols-outlined">assignment</span>
                <span>성향 테스트</span>
              </button>
              <button
                onClick={() => navigateTo('recommendations')}
                className={`w-full text-left px-4 py-2 rounded flex items-center space-x-2 transition ${
                  currentPage === 'recommendations'
                    ? 'bg-blue-50 dark:bg-blue-900 text-primary'
                    : 'text-text-primary-light dark:text-text-primary-dark hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <span className="material-symbols-outlined">people</span>
                <span>맞춤 추천</span>
              </button>
              <button
                onClick={() => navigateTo('dashboard')}
                className={`w-full text-left px-4 py-2 rounded flex items-center space-x-2 transition ${
                  currentPage === 'dashboard'
                    ? 'bg-blue-50 dark:bg-blue-900 text-primary'
                    : 'text-text-primary-light dark:text-text-primary-dark hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <span className="material-symbols-outlined">dashboard</span>
                <span>매칭 현황</span>
              </button>
            </nav>
          )}
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto">
          {currentPage === 'welcome' && <Welcome onNavigate={navigateTo} />}
          {currentPage === 'test' && <PersonalityTest onNavigate={navigateTo} />}
          {currentPage === 'recommendations' && <Recommendations onNavigate={navigateTo} />}
          {currentPage === 'dashboard' && <Dashboard />}
        </main>
      </div>
    </div>
  );
}

export default App;
