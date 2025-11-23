import './TabBar.css';

export type TabId = 'map' | 'story' | 'method';

interface TabBarProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

const TABS: { id: TabId; label: string }[] = [
  { id: 'map', label: 'Map' },
  { id: 'story', label: 'Story' },
  { id: 'method', label: 'Method' },
];

export function TabBar({ activeTab, onTabChange }: TabBarProps) {
  return (
    <nav className="tab-bar" role="tablist" aria-label="Main navigation">
      {TABS.map(({ id, label }) => (
        <button
          key={id}
          role="tab"
          aria-selected={activeTab === id}
          aria-controls={`${id}-tab`}
          className={`tab-button ${activeTab === id ? 'active' : ''}`}
          onClick={() => onTabChange(id)}
        >
          {label}
        </button>
      ))}
    </nav>
  );
}
