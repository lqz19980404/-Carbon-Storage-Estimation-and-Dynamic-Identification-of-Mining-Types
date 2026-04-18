# Carbon Storage Estimation and Dynamic Mining Type Classification System

## Project Description

This project focuses on carbon storage estimation in terrestrial ecosystems and dynamic mining type classification. It integrates a Spatio-Temporal Transformer (STT) model and an XGBoost classifier to analyze carbon dynamics and mining area types.

---

## Models

### 1. Carbon Storage Estimation Model (STT)

File: `STT.py`  
Trained weights: `best_model.pth`

This model is used for estimating carbon storage in terrestrial ecosystems.

- Based on Spatio-Temporal Transformer (STT)
- Uses multi-year remote sensing data (2015–2020)
- Captures spatial and temporal variations
- Outputs carbon storage estimation results

---

### 2. Mining Type Classification Model (XGBoost)

File: `XGboost.py`

This model is used for dynamic classification of mining areas.

- Based on XGBoost algorithm
- Integrates multiple feature sources (remote sensing, statistical data, labeled samples)
- Outputs mining type classification results

---

## Data Processing

The repository includes scripts for data preprocessing, including:
- TIFF data processing
- Data normalization and transformation
- Multi-source data alignment

---

## Project Structure
