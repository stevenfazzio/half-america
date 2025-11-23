import { useState, useEffect, useCallback } from 'react';
import { TabBar } from './components/TabBar';
import { MapTab } from './components/MapTab';
import { StoryTab } from './components/StoryTab';
import { MethodTab } from './components/MethodTab';
import { LoadingOverlay } from './components/LoadingOverlay';
import { ErrorOverlay } from './components/ErrorOverlay';
import { useTopoJsonLoader } from './hooks/useTopoJsonLoader';
import { LAMBDA_VALUES } from './types/lambda';
import type { TabId } from './components/TabBar';
import './App.css';

function getTabFromHash(): TabId {
  const hash = window.location.hash.slice(1); // Remove #
  if (hash === 'story' || hash === 'method') {
    return hash;
  }
  return 'map';
}

function App() {
  const { state: loaderState, retry } = useTopoJsonLoader();
  const [activeTab, setActiveTab] = useState<TabId>(getTabFromHash);

  // Sync tab state with URL hash
  useEffect(() => {
    const handleHashChange = () => {
      setActiveTab(getTabFromHash());
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleTabChange = useCallback((tab: TabId) => {
    window.location.hash = tab;
    setActiveTab(tab);
  }, []);

  // Set initial hash if not present
  useEffect(() => {
    if (!window.location.hash) {
      window.location.hash = 'map';
    }
  }, []);

  // Show loading overlay only when Map tab is active and data is loading
  const showLoading = activeTab === 'map' &&
    (loaderState.status === 'loading' || loaderState.status === 'idle');

  // Show error overlay only when Map tab is active and there's an error
  const showError = activeTab === 'map' && loaderState.status === 'error';

  if (showLoading) {
    const loaded = loaderState.status === 'loading' ? loaderState.loaded : 0;
    return (
      <>
        <TabBar activeTab={activeTab} onTabChange={handleTabChange} />
        <LoadingOverlay loaded={loaded} total={LAMBDA_VALUES.length} />
      </>
    );
  }

  if (showError) {
    return (
      <>
        <TabBar activeTab={activeTab} onTabChange={handleTabChange} />
        <ErrorOverlay message={loaderState.error.message} onRetry={retry} />
      </>
    );
  }

  return (
    <div className="app">
      <TabBar activeTab={activeTab} onTabChange={handleTabChange} />
      <MapTab isActive={activeTab === 'map'} loaderState={loaderState} />
      {activeTab === 'story' && <StoryTab />}
      {activeTab === 'method' && <MethodTab />}
    </div>
  );
}

export default App;
