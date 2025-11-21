# Technical Methodology

## 1. Data Sources & Granularity
To solve the resolution issues inherent in county-level maps, this project utilizes **US Census Tracts**.
* **Tracts vs. Counties:** There are approximately 73,000 census tracts in the US, compared to ~3,100 counties. Tracts generally have a population between 1,200 and 8,000 people, providing a much higher fidelity representation of population distribution.
* **Geometry:** TIGER/Line shapefiles will be used for spatial boundaries.
* **Demographics:** ACS (American Community Survey) 5-Year estimates will provide population data.

## 2. Mathematical Formulation

The core problem is a constrained optimization problem.

Let $T$ be the set of all Census Tracts.
For each tract $t_i$, we have:
* $p_i$: Population
* $a_i$: Land Area
* $l_i$: Perimeter Length

We seek a subset $S \subseteq T$ (the "Selected" tracts).

### The Constraint
The selected subset must contain at least half the total population:
$$\sum_{i \in S} p_i \ge 0.5 \times P_{total}$$

### The Objective Function
We aim to minimize a cost function $C(S)$ defined by a tunable parameter $\lambda \in [0, 1]$:

$$C(S) = (1-\lambda) \cdot \text{Area}(S) + \lambda \cdot \text{Perimeter}(S)$$

Where:
* $\text{Area}(S) = \sum_{i \in S} a_i$
* $\text{Perimeter}(S)$ is the length of the boundary between the set $S$ and the set of unselected tracts $T \setminus S$. Note that internal boundaries between two selected tracts do *not* count toward the perimeter.

### Dimensional Analysis & Normalization
A naive combination of Area ($km^2$) and Perimeter ($km$) is mathematically invalid due to unit mismatch. To resolve this, we introduce a characteristic length scale $\rho$:

$$\rho = \text{median}(\sqrt{a_i})$$

The normalized objective function becomes:
$$\text{Minimize } \quad (1-\lambda) \sum_{i \in S} a_i + \lambda \sum_{(i,j) \in \delta S} \frac{L_{ij}}{\rho}$$

Where $L_{ij}$ is the length of the shared border between a selected tract $i$ and an unselected tract $j$.

## 3. Algorithmic Approach: Max-Flow Min-Cut

This problem can be modeled as a **Graph Cut** problem, solvable via the Max-Flow Min-Cut theorem. This ensures a global optimum for a given $\lambda$, avoiding the local optima traps of greedy region-growing algorithms.

### Graph Construction
We construct a graph $G = (V, E)$ where $V$ contains a node for each tract, plus a Source node ($s$) and a Sink node ($t$).

1.  **Nodes:** Every Census Tract is a node.
2.  **Edges (Neighborhoods):** Adjacent tracts $i$ and $j$ are connected by an edge with capacity proportional to the "smoothness" cost (shared boundary length).
    * $Capacity(i, j) \propto \lambda \cdot \text{SharedBoundaryLength}_{ij}$
3.  **Terminal Edges (Data Term):**
    * Edges connecting to the Source/Sink represent the "cost" of including or excluding a tract based on its Area and Population density.
    * Since the population constraint is global (Hard constraint), it is typically incorporated via Lagrangian Relaxation (converting the constraint into a price $\mu$ included in the edge weights).

### Optimization Process
1.  **Adjacency Graph:** Build a spatial index of all tracts using libraries like `PySAL` or `NetworkX` derived from `GeoPandas` adjacencies.
2.  **Iterative Solver:** For a discrete set of $\lambda$ values (e.g., 0.0, 0.05, ... 1.0):
    * Construct the Flow Network.
    * Solve for the Minimum Cut using `PyMaxFlow` or `scikit-image` graph cut implementations.
    * The cut separates the graph into $S$ (Selected) and $T \setminus S$ (Unselected).

## 4. Post-Processing & Visualization Pipeline

Raw output from the optimization is a list of 30,000+ disconnected tract IDs. To make this performant for the web:

1.  **Dissolve:** For each $\lambda$ solution, merge selected tracts into unified geometries (Polygons/MultiPolygons) using `shapely.ops.unary_union`. This eliminates internal boundaries and drastically reduces vertex count.
2.  **Simplification:** Apply Visvalingam-Whyatt or Douglas-Peucker simplification to reduce file size further.
3.  **Format:** Export as TopoJSON or GeoBuf for optimal web delivery.
4.  **Frontend:** A React application using Mapbox GL JS or Leaflet will load the appropriate geometry file based on the user's slider input.

## 5. Implementation Stack (Planned)
* **Data Ingestion:** `pandas`, `geopandas`, `cenpy` (Census API).
* **Graph Logic:** `networkx`, `scipy.sparse`.
* **Optimization:** `PyMaxFlow` (or `maxflow` wrapper).
* **Geometry Ops:** `shapely`, `topojson`.
* **Web:** React, Mapbox GL JS.
