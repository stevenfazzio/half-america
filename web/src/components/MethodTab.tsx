import 'katex/dist/katex.min.css';
import TeX from '@matejmazur/react-katex';
import './MethodTab.css';

export function MethodTab() {
  const handleTabClick = (tab: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    window.location.hash = tab;
  };

  return (
    <div className="method-tab" role="tabpanel" id="method-tab" aria-labelledby="method">
      <div className="method-content">
        <h1>Methodology</h1>
        <p className="subtitle">Technical details for replication, critique, and extension</p>

        <p className="hook">
          This project frames population visualization as a constrained optimization problem,
          solved exactly using max-flow min-cut.
        </p>

        {/* Objective Function - Prominent */}
        <div className="equation-hero">
          <h2>The Objective Function</h2>
          <p>
            We seek a binary partition where <TeX math="x_i \in \{0, 1\}" /> indicates
            whether tract <TeX math="i" /> is selected. The energy function balances
            three competing terms:
          </p>
          <div className="equation-block">
            <TeX block math={`
              E(X) = \\underbrace{\\lambda \\sum_{(i,j) \\in N} \\frac{\\ell_{ij}}{\\rho} |x_i - x_j|}_{\\text{Boundary Cost}}
              + \\underbrace{(1-\\lambda) \\sum_i \\frac{a_i}{\\rho^2} x_i}_{\\text{Area Cost}}
              - \\underbrace{\\mu \\sum_i p_i x_i}_{\\text{Population Reward}}
            `} />
          </div>
          <div className="equation-legend">
            <p>
              <strong><TeX math="\lambda \in [0, 1)" /></strong> — User-controlled "surface tension" (the slider).
              Higher values favor smooth boundaries over minimal area.
            </p>
            <p>
              <strong><TeX math="\mu" /></strong> — Lagrange multiplier tuned via binary search
              to satisfy the 50% population constraint.
            </p>
            <p>
              <strong><TeX math="\rho = \text{median}(\sqrt{a_i})" /></strong> — Characteristic
              length scale for dimensional consistency.
            </p>
          </div>
        </div>

        <hr className="section-divider" />

        {/* Variable Definitions */}
        <h2>Variable Definitions</h2>
        <p>For each Census Tract <TeX math="t_i" /> in the set <TeX math="T" /> (~73,000 tracts):</p>
        <div className="variable-list">
          <p><TeX math="p_i" /> — Population</p>
          <p><TeX math="a_i" /> — Land area</p>
          <p><TeX math="\ell_{ij}" /> — Length of shared boundary between adjacent tracts <TeX math="i" /> and <TeX math="j" /></p>
        </div>

        <hr className="section-divider" />

        {/* Algorithm */}
        <h2>Algorithm: Max-Flow Min-Cut</h2>
        <p>
          We solve for the global optimum using the max-flow min-cut theorem, avoiding
          local optima common in greedy region-growing algorithms.
        </p>

        <div className="section-card">
          <h3>Graph Construction (s-t Cut)</h3>
          <p>
            We construct a flow network with a Source (selected) and Sink (unselected):
          </p>
          <p>
            <strong>Neighborhood edges (n-links):</strong> Connect adjacent tracts with
            capacity <TeX math="w_{ij} = \lambda \cdot \ell_{ij} / \rho" />.
            Cutting creates a boundary; high-capacity edges encourage smoothness.
          </p>
          <p>
            <strong>Terminal edges (t-links):</strong> Source edges have
            capacity <TeX math="\mu \cdot p_i" /> (selection reward).
            Sink edges have capacity <TeX math="(1-\lambda) \cdot a_i / \rho^2" /> (area cost).
          </p>
        </div>

        <div className="section-card">
          <h3>Binary Search for <TeX math="\mu" /></h3>
          <p>
            Since the population constraint (<TeX math="\sum p_i \approx 0.5 P_{\text{total}}" />)
            is hard but graph cuts are soft, we use binary search:
          </p>
          <p>
            1. Set bounds <TeX math="[\mu_{\min}, \mu_{\max}]" /><br />
            2. Construct graph with current <TeX math="\mu" /><br />
            3. Solve max-flow<br />
            4. If <TeX math="P_{\text{selected}} < P_{\text{target}}" />, increase <TeX math="\mu" /><br />
            5. Repeat until <TeX math="|P_{\text{selected}} - P_{\text{target}}| < \epsilon" />
          </p>
        </div>

        <hr className="section-divider" />

        {/* Data Sources */}
        <h2>Data Sources</h2>
        <p>
          <strong>US Census Bureau TIGER/Line Shapefiles</strong> and <strong>ACS 5-Year Estimates</strong> provide
          tract geometries and population data. At ~73,000 tracts (vs. ~3,100 counties), this offers
          population resolution of 1,200–8,000 people per unit.
        </p>
        <p>
          Raw shapefiles undergo topological cleaning: coordinates are quantized to eliminate
          micro-gaps, and geometries are validated to fix self-intersections before graph construction.
        </p>

        <hr className="section-divider" />

        {/* Post-Processing */}
        <h2>Post-Processing</h2>
        <p>
          The raw output (~30,000+ tract IDs) is processed for web rendering:
        </p>
        <p>
          <strong>Dissolve</strong> — Merge selected tracts into unified MultiPolygon geometries.<br />
          <strong>Simplify</strong> — Douglas-Peucker simplification (500m tolerance) reduces vertices ~98%.<br />
          <strong>Export</strong> — TopoJSON encoding preserves shared topology, preventing rendering gaps.
        </p>

        <hr className="section-divider" />

        {/* Implementation Stack */}
        <h2>Implementation Stack</h2>
        <div className="stack-list">
          <p><strong>Data:</strong> pandas, cenpy (Census API)</p>
          <p><strong>Spatial:</strong> geopandas, libpysal (adjacency graphs)</p>
          <p><strong>Optimization:</strong> PyMaxFlow (C++ graph cuts)</p>
          <p><strong>Geometry:</strong> shapely, topojson</p>
          <p><strong>Web:</strong> React, MapLibre GL JS, deck.gl</p>
        </div>

        <hr className="section-divider" />

        {/* Navigation */}
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
  );
}
