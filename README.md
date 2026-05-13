# Research Flow Pipeline

A generalized framework for end-to-end scientometric research and AI-driven analysis of scholarly communication.

## Key Features

- **Automated Data Processing**: Clean and normalize research datasets from multiple sources.
- **AI-Driven Interpretation**: Leverage LLMs for topic modeling and trend analysis.
- **Scientometric Visualizations**: Generate manuscript-ready figures and network maps.
- **Multi-Phase Pipeline**: Structured workflow from raw data to final research report.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/amarnath3003/research-flow.git
   cd research-flow
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama** (for AI interpreter):
   Ensure [Ollama](https://ollama.ai/) is installed and running locally.

## Quick Start

To run the entire pipeline automatically:

```powershell
python run_research_pipeline.py all-auto
```

This will perform the base data fetch, cleaning, and generate initial topic classifications.

## Project Structure

- `scientometric_pipeline/`: Core scripts for bibliometric analysis.
- `advanced_pipeline/`: AI-driven interpretation and complex analytics.
- `phase1_refinement/`: Topic classification and data cleaning.
- `phase2_validation/`: Manual curation and theme merging logic.
- `phase3_analysis/`: Quantitative metrics and trend detection.
- `phase4_interpretation/`: LLM-assisted qualitative analysis.
- `phase5_visualizations/`: Generation of all charts and maps.
- `FinalOutputs/`: Directory containing all generated reports and data.




