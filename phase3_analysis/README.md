# Phase 3: Core Scientometric Analysis

This directory contains the scripts required to generate quantitative results for your scientometric study.

## Prerequisites
- `pandas`, `matplotlib`, `numpy`

## Analysis Scripts

### 1. Publication Trends (`step1_trend_analysis.py`)
- **What it does**: Plots annual publication counts and calculates CAGR.
- **Key Metrics**: CAGR for full period and segmented eras.
- **Outputs**:
  - `outputs/trends/publication_trend.png`
  - `outputs/trends/trend_summary.csv`

### 2. Source Influence (`step2_source_analysis.py`)
- **What it does**: Identifies top journals and sources.
- **Key Metrics**: Paper count, total citations, Source H-index.
- **Outputs**:
  - `outputs/sources/top_sources.csv`

### 3. Geopolitical Mapping (`step3_geopolitical_analysis.py`)
- **What it does**: Extracts country data and collaboration patterns.
- **Key Metrics**: MCP vs SCP ratio.
- **Outputs**:
  - `outputs/geopolitical/country_collaboration.csv`

### 4. Network Analysis (`step4_network_analysis.py`)
- **What it does**: Maps the intellectual structure via keyword co-occurrence.
- **Outputs**:
  - `outputs/networks/keyword_cooccurrence_edges.csv`
  - `outputs/networks/keyword_nodes.csv`

## Execution Order
1. `step1_trend_analysis.py`
2. `step2_source_analysis.py`
3. `step3_geopolitical_analysis.py`
4. `step4_network_analysis.py`

## Interpreting Results
- Compare segmented CAGR periods to identify growth accelerations.
- Analyze top sources to understand where the research is published.
- High MCP ratios indicate strong international collaboration.
