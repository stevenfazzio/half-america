import { MarkdownRenderer } from './MarkdownRenderer'
import methodologyContent from '../../../METHODOLOGY.md?raw'
import './MethodTab.css'

export function MethodTab() {
  const handleTabClick = (tab: string) => (e: React.MouseEvent) => {
    e.preventDefault()
    window.location.hash = tab
  }

  return (
    <div className="method-tab" role="tabpanel" id="method-tab" aria-labelledby="method">
      <div className="method-content">
        <MarkdownRenderer content={methodologyContent} />

        {/* Navigation - kept as JSX for interactivity */}
        <hr className="section-divider" />
        <h2>Explore</h2>
        <div className="tab-links">
          <a href="#map" className="tab-link" onClick={handleTabClick('map')}>
            View the Interactive Map →
          </a>
          <a href="#story" className="tab-link" onClick={handleTabClick('story')}>
            Read the Story →
          </a>
        </div>

        <p className="repo-link">
          <a
            href="https://github.com/stevenfazzio/half-america"
            target="_blank"
            rel="noopener noreferrer"
          >
            View full source on GitHub →
          </a>
        </p>
      </div>
    </div>
  )
}
