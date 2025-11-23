import './StoryTab.css';

export function StoryTab() {
  const handleTabClick = (tab: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    window.location.hash = tab;
  };

  return (
    <div className="story-tab" role="tabpanel" id="story-tab" aria-labelledby="story">
      <div className="story-content">
        <h1>Half of America</h1>
        <p className="subtitle">Where do half of all Americans actually live?</p>

        <p className="hook">
          What if half of all Americans lived in an area smaller than you'd expect?
        </p>

        <h2>The Surprising Answer</h2>
        <p>
          Half of the United States population—over <span className="stat-highlight">165 million people</span>—lives
          in just <span className="stat-highlight">1.1% of the country's land area</span>. That's roughly the size of Virginia.
        </p>
        <p>
          The blue shapes on the map represent these areas: dense urban cores and their
          surrounding suburbs where Americans have concentrated. The rest of the country? Mostly empty.
        </p>

        <hr className="section-divider" />

        <h2>Why This Map Looks Different</h2>
        <p>
          You've probably seen maps like this before. They usually show counties, and they
          usually look wrong. Here's why we took a different approach:
        </p>

        <div className="section-card">
          <h3>The San Bernardino Problem</h3>
          <p>
            San Bernardino County, California is larger than nine US states. It's also mostly
            desert. When you highlight it on a "half of America" map, you're including
            thousands of square miles where almost nobody lives.
          </p>
        </div>

        <div className="section-card">
          <h3>Going Smaller: Census Tracts</h3>
          <p>
            We used Census Tracts instead—about 73,000 small neighborhoods across the country.
            This gives us much higher resolution, but creates a new problem: thousands of
            tiny disconnected dots that are hard to visually process.
          </p>
        </div>

        <div className="section-card">
          <h3>Finding the Shape</h3>
          <p>
            The solution was to let the boundaries find themselves. Using an optimization
            technique from computer vision, we minimize the <em>perimeter</em> of the selected
            regions. This produces smooth, organic shapes that are both accurate and visually clear.
          </p>
        </div>

        <div className="image-placeholder">
          [Evolution diagram: County → Tracts → Bridges → Smooth - Coming in Phase 6]
        </div>

        <hr className="section-divider" />

        <h2>The Smoothness Slider</h2>
        <p>
          The slider on the map controls a tradeoff between precision and visual clarity:
        </p>
        <p>
          <strong>Low values</strong> give you maximum precision. You see every dense
          neighborhood, but as scattered dots that are hard to reason about.
        </p>
        <p>
          <strong>High values</strong> give you maximum smoothness. The regions merge into
          coherent shapes that reveal the overall pattern of where Americans live.
        </p>
        <p>
          There's no "correct" setting—it depends on what you want to see.
        </p>

        <hr className="section-divider" />

        <h2>Explore</h2>
        <div className="tab-links">
          <a href="#map" className="tab-link" onClick={handleTabClick('map')}>
            View the Interactive Map →
          </a>
          <a href="#method" className="tab-link" onClick={handleTabClick('method')}>
            Read the Full Methodology →
          </a>
        </div>
      </div>
    </div>
  );
}
