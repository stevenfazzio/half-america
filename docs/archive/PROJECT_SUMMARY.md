> **ARCHIVED**: This document has been archived as of 2025-01-20. It is a static historical
> record and should not be updated. Current project documentation can be found in:
> - [README.md](../../README.md) - Project overview and quick start
> - [METHODOLOGY.md](../../METHODOLOGY.md) - Technical methodology
> - [ROADMAP.md](../../ROADMAP.md) - Implementation roadmap

---

# Half of America: A Topology Optimization Experiment

## Background & Inspiration
There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties." An example of this can be seen in this [Business Insider article](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9).

These maps serve a simple purpose: they illustrate the extreme geographic concentration of the US population. The methodology is usually a simple sorting algorithm:
1. Rank all counties by population.
2. Select the top $N$ counties until the cumulative sum exceeds 50% of the total US population.

## The Problem
While effective at shock value, the standard "County-Level" approach suffers from significant cartographic and logical flaws:

1.  **The San Bernardino Problem:** These maps almost always include San Bernardino County, CA. While populous, this county is geographically massive (larger than nine US states) and primarily composed of empty desert. Including the entire county implies the desert is densely populated, violating the visual integrity of the map.
2.  **The "Dust" Problem:** If we attempt to fix the resolution issue by moving to smaller units (like Census Tracts) and simply ranking by density, the map dissolves into "dust"—thousands of tiny, disconnected specks. While mathematically accurate, it fails as a visualization of human settlement patterns, which naturally form continuous regions.

## Project Goal
The goal of this project is to create an interactive web application that solves the "Half of America" problem using **topology optimization**.

Instead of simply selecting high-density areas, we will optimize for a weighted combination of **Density (Area)** and **Compactness (Perimeter)**. This allows us to view the US population not as a histogram, but as a series of organic shapes that behave according to a "surface tension" parameter.

### The User Experience
The final output will be a web-based map of the Continental United States featuring a slider control.
* **The Slider:** Controls a parameter $\lambda$ (lambda).
* **$\lambda \approx 0$:** The map minimizes **Area**. The result is a high-resolution, "dusty" map of city centers and dense suburbs.
* **$\lambda \approx 1$:** The map minimizes **Perimeter**. The result is a set of highly compact, smooth "blobs" that sacrifice some density to maintain continuous shapes.

By sliding between these values, the user can visualize the "surface tension" of American geography, observing how distinct urban centers merge into megaregions and eventually into continental blocks.

## Scope
* **Geography:** Contiguous United States (lower 48).
* **Data Source:** US Census Bureau (Census Tract level).
* **Technical constraints:** Due to the computational complexity of the optimization, the map states for various $\lambda$ values will be pre-calculated. The web app will serve as a visualizer for these pre-computed geometries.

## Project Status & Disclaimer
This is a personal experimental project, created to explore concepts in topology optimization and cartography. It is not intended as a production-grade analytical tool, nor should it be used for official demographic planning. The data visualizations are approximations based on pre-computed optimization states.
