# Technical Methodology

## Motivation

Traditional "half of America" visualizations face several technical limitations:

1. **County Resolution**: County boundaries encompass vast unpopulated areas. San Bernardino County, for example, exceeds the land area of nine US states while containing primarily desert terrain.

2. **Dust Artifacts**: Using finer-grained units (e.g., Census Tracts) produces thousands of disconnected micro-regions. While mathematically accurate, this exceeds human perceptual limits for visual reasoning.

3. **Bridge Artifacts**: Minimizing region *count* to consolidate dust produces degenerate geometries with narrow "bridge" connections between dense population centers.

This methodology addresses these issues by minimizing *perimeter* rather than region count, producing smooth, topologically coherent shapes that remain accurate representations of population concentration.

## 1. Data Sources & Preprocessing
To address the resolution limits of county-level maps, this project utilizes **US Census Tracts**.

### 1.1 Granularity
* **Source:** US Census Bureau TIGER/Line Shapefiles and ACS 5-Year Estimates.
* **Scale:** ~73,000 tracts (vs. ~3,100 counties). Tracts offer a population resolution of 1,200–8,000 people, providing high-fidelity density data.

### 1.2 Topological Cleaning
Raw census shapefiles often contain "slivers," overlaps, and self-intersections that break graph adjacency logic.
* **Quantization:** Coordinates will be snapped to a high-precision integer grid (via TopoJSON) to eliminate micro-gaps between tracts.
* **Validation:** All geometries are passed through `shapely.make_valid()` to fix self-intersections and ensure valid polygon topology before graph construction.

## 2. Mathematical Formulation

The problem is modeled as a **Constrained Optimization** problem on a discrete spatial graph.

Let $T$ be the set of all Census Tracts. For each tract $t_i$, we define:
* $p_i$: Population
* $a_i$: Land Area
* $l_{ij}$: Length of the shared boundary between tracts $i$ and $j$.

### 2.1 Dimensional Analysis
To minimize a weighted sum of Area ($km^2$) and Perimeter ($km$), we must normalize units. We introduce a characteristic length scale $\rho$:

$$\rho = \text{median}(\sqrt{a_i})$$

This ensures both terms in the objective function are dimensionless.

### 2.2 The Objective Function (Lagrangian Relaxation)
We seek a binary partition of the graph where $x_i \in \{0, 1\}$ indicates whether tract $i$ is selected ($1$) or unselected ($0$).

We aim to minimize the energy $E(X)$ composed of three terms: **Compactness**, **Area**, and a **Population Reward**.

$$E(X) = \underbrace{\lambda \sum_{(i,j) \in N} \frac{l_{ij}}{\rho} \cdot |x_i - x_j|}_{\text{Boundary Cost}} + \underbrace{(1-\lambda) \sum_{i} \frac{a_i}{\rho^2} x_i}_{\text{Area Cost}} - \underbrace{\mu \sum_{i} p_i x_i}_{\text{Population Reward}}$$

Where:
* $\lambda \in [0, 1)$: User-controlled "Surface Tension" parameter. Note: $\lambda = 1$ is excluded because it causes the area cost term $(1-\lambda)$ to vanish, making the Lagrangian relaxation degenerate.
* $\mu$: The Lagrange multiplier enforcing the population constraint.

## 3. Algorithmic Approach: Max-Flow Min-Cut

We solve for the global optimum using the **Max-Flow Min-Cut** theorem. This avoids local optima common in greedy region-growing algorithms.

### 3.1 Graph Construction ($s-t$ Cut)
We construct a flow network $G = (V, E)$ with a Source ($S$, selected) and Sink ($T$, unselected).

1.  **Neighborhood Edges (n-links):**
    * Connect adjacent tracts $i$ and $j$.
    * **Capacity:** $w_{ij} = \lambda \cdot \frac{l_{ij}}{\rho}$
    * *Logic:* Cutting this edge creates a boundary; high capacity edges (long borders) are harder to cut, encouraging smoothness.
2.  **Terminal Edges (t-links):**
    * **Source Edge $(s, i)$:** Represents the "reward" for selecting tract $i$.
        * Capacity: $\mu \cdot p_i$
    * **Sink Edge $(i, t)$:** Represents the "cost" of including tract $i$'s area.
        * Capacity: $(1-\lambda) \cdot \frac{a_i}{\rho^2}$

### 3.2 Nested Optimization Strategy
Since the population constraint ($\sum p_i \approx 0.5 P_{total}$) is hard, but graph cuts are soft, we employ a nested solver:

1.  **Outer Loop (The User Slider):** Iterate through target $\lambda$ values (e.g., $0.0, 0.1, \dots 1.0$).
2.  **Inner Loop (The Constraint Tuner):**
    * We define a target population $P_{target} = 0.5 \times P_{total}$.
    * Since the selected population is monotonic with respect to $\mu$, we use **Binary Search** to find the optimal $\mu$.
    * **Step 1:** Set bounds $[\mu_{min}, \mu_{max}]$.
    * **Step 2:** Construct graph with current $\mu$.
    * **Step 3:** Solve Max-Flow.
    * **Step 4:** Check resulting population sum.
        * If $P_{selected} < P_{target}$, increase $\mu$ (Selection reward is too low).
        * If $P_{selected} > P_{target}$, decrease $\mu$ (Selection reward is too high).
    * **Step 5:** Repeat until $|P_{selected} - P_{target}| < \epsilon$ (tolerance).

## 4. Post-Processing & Visualization

The raw output is a list of 30,000+ disconnected tract IDs. To render this efficiently on the web:

1.  **Dissolve:** Merge selected tracts into unified `MultiPolygon` geometries using `shapely.ops.unary_union`.
2.  **Simplification:** Apply Douglas-Peucker simplification to reduce vertex count while preserving shape topology.
3.  **Export:** Save geometry as **TopoJSON**. This format is crucial as it encodes shared topology, preventing gaps from appearing between shapes during rendering.

The simplification step uses a tolerance of 500 meters (in the projected coordinate system), which achieves approximately 98% vertex reduction while preserving visual fidelity at typical web map zoom levels. The final TopoJSON export transforms coordinates from the equal-area projection (EPSG:5070) to WGS84 (EPSG:4326) for web map compatibility.

## 5. Implementation Stack

* **Data Ingestion:** `pandas`, `cenpy` (Census API).
* **Spatial Logic:** `geopandas`, `libpysal` (for robust adjacency weights/graph building).
* **Optimization:** `PyMaxFlow` (fast C++ wrapper for graph cuts).
* **Geometry Ops:** `shapely`, `topojson`.
* **Web:** React, Mapbox GL JS (basemap), deck.gl (data visualization).
