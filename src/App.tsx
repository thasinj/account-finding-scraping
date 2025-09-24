import { useMemo, useState } from 'react';
import { Container, Theme } from './settings/types';
import InstagramProfilesTable from './components/generated/InstagramProfilesTable';
import DiscoveryDashboard from './components/DiscoveryDashboard';
import RunsHistory from './components/RunsHistory';
import ProfilesDatabase from './components/ProfilesDatabase';

let theme: Theme = 'light';
let container: Container = 'none';

function App() {
  const [activeTab, setActiveTab] = useState('discovery');

  function setTheme(theme: Theme) {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  setTheme(theme);

  const generatedComponent = useMemo(() => {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex space-x-8">
              <button
                onClick={() => setActiveTab('discovery')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'discovery'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                🔍 Discovery Dashboard
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'history'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                📊 Runs History
              </button>
              <button
                onClick={() => setActiveTab('profiles')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'profiles'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                👤 Profiles Database
              </button>
            </div>
          </div>
        </nav>

        {/* Content */}
        <div className="max-w-7xl mx-auto">
          {activeTab === 'discovery' && <DiscoveryDashboard />}
          {activeTab === 'history' && <RunsHistory />}
          {activeTab === 'profiles' && <ProfilesDatabase />}
        </div>
      </div>
    );
  }, [activeTab]);

  if (container === 'centered') {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center">
        {generatedComponent}
      </div>
    );
  } else {
    return generatedComponent;
  }
}

export default App;
