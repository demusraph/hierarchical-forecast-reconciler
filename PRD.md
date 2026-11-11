# PRD: Hierarchical Forecast Reconciler (HFR)

## 1. Executive Summary & Problem-Solution Fit
The **Hierarchical Forecast Reconciler (HFR)** is a high-performance engine designed to enforce mathematical coherence across multi-level time-series forecasts. In large-scale supply chain and financial planning, independent models (e.g., ARIMA, Prophet, XGBoost) applied at different granularities (e.g., SKU vs. Category) produce incoherent results where the sum of parts does not equal the whole. HFR solves this by applying optimal linear projection operators (MinT) to reconcile base forecasts, minimizing the trace of the reconciled forecast error covariance matrix.

## 2. Target Personas & Core User Stories
*   **Data Scientist:** "As a Data Scientist, I want to inject my base forecasts into a structured reconciliation pipeline so that I can ensure global consistency without retraining individual models."
*   **Supply Chain Analyst:** "As an Analyst, I want to visualize the coherence gap between my bottom-up and top-down forecasts so that I can identify which nodes in the hierarchy are contributing most to forecast variance."
*   **ML Engineer:** "As an ML Engineer, I want a RESTful API to reconcile batch forecasts in real-time so that downstream ERP systems receive coherent data for procurement planning."

## 3. MoSCoW Feature Matrix

| Priority | Feature | Description |
| :--- | :--- | :--- |
| **P0** | S-Matrix Generator | Automated construction of the summation matrix from hierarchical string tokens (e.g., `['Total', 'Region', 'Store']`). |
| **P0** | MinT Estimators | Implementation of OLS, WLS, and Sample Covariance reconciliation operators. |
| **P0** | Core Engine | NumPy/SciPy-based linear algebra solver for $y_{rec} = S(S^T W S)^{-1} S^T W \hat{y}$. |
| **P1** | Shrinkage Estimators | Ledoit-Wolf and Oracle Approximating Shrinkage (OAS) for covariance matrix regularization. |
| **P1** | REST API | FastAPI-based endpoints for `/reconcile` (batch) and `/stream` (async). |
| **P1** | Audit Module | Automated calculation of coherence gaps and variance reduction metrics. |
| **P2** | Visualization | Interactive dashboard (Plotly/Dash) for hierarchical tree traversal and error auditing. |
| **P2** | Persistence | Support for Parquet/Delta Lake I/O for large-scale hierarchical datasets. |

## 4. Non-Functional Requirements
*   **Latency (p95):** < 200ms for a hierarchy of 10,000 nodes and 52 time-steps.
*   **Memory Footprint:** Must support "Streaming Reconciliation" mode where the covariance matrix is computed in chunks to avoid $O(N^2)$ memory explosion on large hierarchies.
*   **Numerical Stability:** Use SVD-based inversion for $S^T W S$ to handle rank-deficient covariance matrices.
*   **Offline-Readiness:** The core reconciliation library must be installable via `pip` without requiring external database dependencies.
*   **Type Safety:** 100% Python type-hinted (PEP 484) with `mypy` strict mode enabled.

## 5. Quantitative Success Metrics & KPIs
*   **Coherence Error:** Reduction of the sum of squared differences between aggregate nodes and the sum of their children to near-zero (floating-point epsilon).
*   **Variance Reduction:** Measured as the ratio of the trace of the reconciled error covariance matrix to the trace of the base forecast error covariance matrix (Target: < 1.0).
*   **Throughput:** Ability to reconcile 100,000 nodes per second on a standard 8-core CPU instance.
*   **API Reliability:** 99.99% uptime for the reconciliation service with a 5xx error rate < 0.01%.