# Phase 3: Core Scientometric Analysis

This directory contains the scripts required to generate the quantitative results for the scientometric study on Scholarly Communication and Research Security.

## Prerequisites
- `pandas`
- `matplotlib`
- `numpy`

## Analysis Scripts

### 1. Publication Trends (`step1_trend_analysis.py`)
- **What it does**: Plots annual publication counts from 2010 to 2024.
- **Key Metrics**: CAGR (Compound Annual Growth Rate) for the full period, pre-2020, and post-2020.
- **Outputs**:
  - `outputs/trends/publication_trend.png`: A high-resolution plot with COVID-era segmentation.
  - `outputs/trends/trend_summary.csv`: Summary of CAGR and growth metrics.

### 2. Source Influence (`step2_source_analysis.py`)
- **What it does**: Identifies top journals and sources.
- **Key Metrics**: Paper count, total citations, and **Source H-index** (dataset-specific).
- **Outputs**:
  - `outputs/sources/top_sources.csv`: Top 50 journals ranked by H-index.

### 3. Geopolitical Mapping (`step3_geopolitical_analysis.py`)
- **What it does**: Extracts country data from author/affiliation fields.
- **Key Metrics**: MCP (Multiple Country Publications) vs SCP (Single Country Publications) ratio.
- **Outputs**:
  - `outputs/geopolitical/country_collaboration.csv`: Ranking of countries and their collaboration patterns.

### 4. Network Analysis (`step4_network_analysis.py`)
- **What it does**: Maps the intellectual structure via keyword co-occurrence.
- **Outputs**:
  - `outputs/networks/keyword_cooccurrence_edges.csv`: Edge list for visualization in VOSviewer or Gephi.
  - `outputs/networks/keyword_nodes.csv`: Node list with frequency data.

## Execution Order
1. Run `step1_trend_analysis.py`
2. Run `step2_source_analysis.py`
3. Run `step3_geopolitical_analysis.py`
4. Run `step4_network_analysis.py`

## Interpreting Results for the Paper
- **Discussion Point 1**: Does the Post-2020 CAGR show a significant acceleration compared to Pre-2020? This supports the "COVID as a catalyst for research security" hypothesis.
- **Discussion Point 2**: Are cybersecurity journals (e.g., *Journal of Cybersecurity*) or library science journals (e.g., *Journal of Librarianship and Scholarly Communication*) more dominant?
- **Discussion Point 3**: High MCP ratios indicate strong international collaboration, while low ratios suggest domestic-centric research security policies.
