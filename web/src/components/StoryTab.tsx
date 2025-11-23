import './StoryTab.css';

export function StoryTab() {
  return (
    <div className="story-tab" role="tabpanel" id="story-tab" aria-labelledby="story">
      <div className="story-content">
        <h1>The Story</h1>
        <p className="subtitle">How half of America fits in a surprisingly small space</p>
        <div className="placeholder">
          <p>Content coming soon.</p>
          <p>This tab will explain the intuition behind the visualization without the math.</p>
        </div>
      </div>
    </div>
  );
}
