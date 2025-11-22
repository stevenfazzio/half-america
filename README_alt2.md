# Half of America

## Introduction

A brief hook explaining what this project does: an interactive data visualization showing where 50% of Americans live using topology optimization. This section should capture attention and explain the core value proposition in 2-3 sentences.

### The Problem

Explains the limitations of traditional "half of America" maps: the San Bernardino Problem (huge sparse counties) and the Dust Problem (too many tiny disconnected regions). This motivates why a new approach is needed.

### The Solution

Describes the topology optimization approach that balances area minimization vs. perimeter smoothness using a "surface tension" parameter (λ). Explains how this produces smooth, organic shapes instead of dust or oversized regions.

## Quick Start

### Prerequisites

Lists what users need before installation: Python version, system requirements, and any external dependencies.

### Installation

Step-by-step instructions for installing the package via pip/uv, including the package name and any optional dependency groups.

### Basic Usage

Shows the simplest way to run the CLI to generate results. Should include 2-3 example commands that demonstrate core functionality (precompute, export).

## How It Works

### The Algorithm

High-level explanation of the Max-Flow Min-Cut optimization approach. Explains the two key parameters: λ (user-controlled surface tension) and μ (Lagrange multiplier for population constraint). Should be accessible to non-technical readers.

### Data Sources

Describes the Census Bureau data used: TIGER/Line Shapefiles for geometry and ACS 5-Year Estimates for population. Mentions the ~73,000 Census Tract resolution.

### The λ Parameter

Explains what the lambda slider controls: λ≈0 produces dusty high-resolution maps, λ≈0.9 produces smooth compact blobs. Include visual descriptions or link to examples.

## Usage

### CLI Reference

Complete reference for all CLI commands with options and examples. Should cover `precompute`, `export`, and any other commands with their flags.

### Python API

Brief overview of programmatic usage with import examples. Links to full API documentation for detailed reference.

### Cache Management

Explains the caching system, where cached data lives, when to clear caches, and how to force rebuilds.

## Project Structure

### Directory Layout

Shows the file/folder structure of the repository with brief descriptions of key directories (src/, data/, docs/, tests/).

### Data Files

Explains the data directory structure, what gets cached where, and the naming conventions for cached files that include year keys.

## Development

### Setup

Instructions for setting up a development environment, including cloning, installing dev dependencies, and running the test suite.

### Testing

How to run tests, including commands for running specific tests, skipping integration tests, and running tests matching patterns.

### Code Quality

Commands for linting, formatting, and type checking. Lists the tools used (ruff, mypy).

## Documentation

### Technical Methodology

Points to METHODOLOGY.md for the full mathematical formulation, including the objective function, graph construction details, and nested optimization strategy.

### API Reference

Points to docs/API.md for complete Python API documentation covering all modules.

### Roadmap

Points to ROADMAP.md for implementation phases and future enhancement ideas.

## License

Specifies the project license and any relevant copyright information.

## Acknowledgments

Credits data sources (US Census Bureau), key libraries used, and any inspirations or related work.
