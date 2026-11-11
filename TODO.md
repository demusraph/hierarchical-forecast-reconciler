# Production Task Roadmap & Execution Checklist: Hierarchical Forecast Reconciler

This document serves as the operational engineering checklist and architectural execution plan for building, verifying, and releasing the `hierarchical-forecast-reconciler` library.

---

## Progress Overview

| Phase | Description | Status | Completion |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Architecture Scaffolding & Foundation | In Progress | 80% |
| **Phase 2** | Core Domain Logic & Engine Implementation | Pending | 0% |
| **Phase 3** | Automated Stress Testing & Verification | Pending | 0% |
| **Phase 4** | Packaging, Documentation & Integration | Pending | 0% |
| **Phase 5** | Release Pipeline & Production Readiness | Pending | 0% |

---

## Phase 1: Architecture Scaffolding & Foundation

Establish the workspace environment, build execution pipelines, define strict type protocols, structural abstractions, and high-performance memory representations for hierarchical graph topologies.

### 1.1 Project & Workspace Setup
- [x] Initialize repository layout using PEP 621 compliant `pyproject.toml` with `hatchling` build-backend.
- [x] Configure Python version constraint to target `>= 3.11, < 3.14`.
- [x] Configure `ruff` for code formatting and strict linting (enforcing `F`, `E`, `W`, `C90`, `I`, `N`, `UP`, `YTT`, `ANN`, `BLE`, `B`, `A`, `COM`, `C4`, `DTZ`, `T10`, `EM`, `EXE`, `ISC`, `ICN`, `PT`, `Q`, `RET504`, `SIM`, `TID`, `ARG`, `PTH`, `ERA`, `PD`, `PL`, `TRY`, `RUF`).
- [x] Configure `mypy` in strict mode (`strict = true`, `disallow_untyped_calls = true`, `warn_return_any = true`, `enable_incomplete_feature = ["Unpack"]`).
- [x] Establish directory tree:
  ```text
  ├── src/
  │   └── forecast_reconciliation/
  │       ├── py.typed
  │       ├── core/
  │       ├── matrix/
  │       ├── estimators/
  │       ├── reconcilers/
  │       ├── validation/
  │       └── io/
  ├── tests/
  │   ├── unit/
  │   ├── integration/
  │   ├── stress/
  │   └── benchmarks/
  ├── docs/
  └── scripts/
  ```

### 1.2 Domain Type Specifications & Exception Hierarchy
- [x] Define custom runtime exception hierarchy inheriting from `ReconcilerError`:
  - [x] `HierarchyStructureError` (cyclic DAGs, orphaned nodes, invalid sum mappings).
  - [x] `DimensionalityMismatchError` (incompatible $S$, $y$, or $W$ dimensions).
  - [x] `SingularMatrixError` (rank-deficient $S^T W^{-1} S$ inversions).
  - [x] `NonPositiveDefiniteError` (invalid base forecast covariance matrix $W$).
  - [x] `ConstraintViolationError` (infeasible bounds in QP solver).
- [ ] Define core Protocols and Type Aliases using `typing.Protocol`, `TypeGuard`, and `numpy.typing.NDArray`:
  - [ ] `NodeID = str | int`
  - [ ] `MatrixSparse = scipy.sparse.csc_matrix | scipy.sparse.csr_matrix`
  - [ ] `VectorFloat = numpy.ndarray[tuple[int], numpy.dtype[numpy.float64]]`
  - [ ] `MatrixFloat = numpy.ndarray[tuple[int, int], numpy.dtype[numpy.float64]]`
  - [ ] `HierarchyMappingProtocol` for structural hierarchy inspection.

### 1.3 Topology & Matrix Foundation
- [ ] Implement `HierarchyGraph` internal data structure based on Sparse Compressed Column/Row representations.
- [ ] Implement Sparse Summing Matrix ($S \in \mathbb{R}^{N \times n_b}$) builder from adjacency lists or parent-child edge mappings.
- [ ] Implement Sparse Constraint Matrix ($C \in \mathbb{R}^{n_a \times N}$) construction where $C = [I_{n_a} \mid -A]$ such that $C y = 0$.
- [ ] Implement validation routines for structural invariants:
  - [ ] Verify Directed Acyclic Graph (DAG) integrity via Kahn's algorithm or Tarjan's strongly connected components.
  - [ ] Check matrix rank condition $\text{rank}(S) = n_b$.
  - [ ] Validate contiguous node index alignment between $S$, $C$, and forecast vectors.
- [ ] Implement memory layout optimizers (`ensure_c_contiguous`, `ensure_csc_format`) to minimize zero-copy bridge overhead with native SciPy/SuiteSparse routines.

---

### Definition of Done: Phase 1
- [x] Dev environment fully functional (`hatch run lint`, `hatch run typecheck` execute cleanly with 0 warnings).
- [x] Core dynamic type definitions, core protocols, and custom exceptions implemented under `src/forecast_reconciliation/core/`.
- [ ] Graph verification logic passing unit tests for trees, grouped hierarchies, and general DAGs.
- [ ] 100% test coverage achieved on `src/forecast_reconciliation/core/` structural utilities.

---

## Phase 2: Core Domain Logic & Engine Implementation

Implement statistical estimation routines, standard reconciliation algorithms, high-performance sparse linear solvers, and empirical risk minimization frameworks.

### 2.1 Covariance Matrix ($\hat{W}$) Estimators
Implement statistical estimators for the base forecast error covariance matrix $\hat{W}_h = \frac{1}{N}\sum_{t=1}^{N} e_t e_t^T$:
- [ ] `IdentityCovariance`: Implements $W = I_{N \times N}$ (OLS reconciliation baseline).
- [ ] `StructuralVariance`: Implements $W = \text{diag}(S \mathbf{1}_{n_b})$ structural scaling (WLS variance proportional to bottom-level child count).
- [ ] `SampleCovariance`: Computes empirical residual covariance $W = \frac{1}{n - 1} E^T E$. Includes zero-variance replacement and epsilon diagonal stabilization.
- [ ] `ShrinkageCovariance`:
  - [ ] Implement Ledoit-Wolf optimal shrinkage toward diagonal target matrix $F = \text{diag}(W)$.
  - [ ] Implement Schäfer-Strimmer shrinkage estimator with intensity parameter calculation:
    $$\lambda^* = \frac{\sum_{i \neq j} \widehat{\text{Var}}(s_{ij})}{\sum_{i \neq j} s_{ij}^2}$$
- [ ] `DiagonalSampleCovariance`: Computes variance-only diagonal estimator $W = \text{diag}(\hat{\sigma}_1^2, \dots, \hat{\sigma}_N^2)$ (MinT-Diag variant).

### 2.2 Unconstrained Linear Reconciliation Solvers
Implement closed-form linear projection operator:
$$\tilde{y} = S P \hat{y} = S (S^T W^{-1} S)^{-1} S^T W^{-1} \hat{y}$$
- [ ] `UnconstrainedLinearReconciler`:
  - [ ] Implement direct solver using Sparse Cholesky decomposition (`scipy.sparse.linalg.factorized` / `CHOLMOD` backend if available).
  - [ ] Implement fallback Sparse LU decomposition (`scipy.sparse.linalg.splu`) with condition number estimation (`rcond`).
  - [ ] Implement explicit projection matrix extraction $P \in \mathbb{R}^{n_b \times N}$ for batch multi-horizon projection $\tilde{Y}_H = S P \hat{Y}_H$.
- [ ] `BottomUpReconciler`:
  - [ ] Construct selection operator $J = [0_{n_b \times n_a} \mid I_{n_b}]$.
  - [ ] Projection $\tilde{y} = S J \hat{y}$.
- [ ] `TopDownReconciler`:
  - [ ] Implement proportion vector assignment $\mathbf{p} \in \mathbb{R}^{n_b}$ where $\sum p_i = 1$.
  - [ ] Proportion calculation strategies:
    - [ ] `HistoricalProportions`: Average historical bottom-level relative to top-level aggregate.
    - [ ] `ForecastProportions`: Ratio of bottom-level base forecasts to aggregated base forecast.
    - [ ] `AverageForecastProportions`: Historical mean of forecast proportions over evaluation windows.
  - [ ] Matrix formulation: $\tilde{y} = S \mathbf{p} \mathbf{e}_1^T \hat{y}$.
- [ ] `MiddleOutReconciler`:
  - [ ] Implement middle-level node selection and subtree decomposition.
  - [ ] Apply top-down proportions below middle level and bottom-up aggregation above middle level.

### 2.3 Constrained & Non-Linear Reconciliation Engine
Implement convex quadratic programming formulation for constrained reconciliation:
$$\min_{\tilde{y}_{b}} \frac{1}{2} (\hat{y} - S \tilde{y}_{b})^T W^{-1} (\hat{y} - S \tilde{y}_{b}) \quad \text{s.t.} \quad G \tilde{y}_{b} \ge h, \quad A \tilde{y}_{b} = b$$
- [ ] `ConstrainedQPReconciler`:
  - [ ] Construct OSQP / OSQP-sparse problem structure natively using sparse matrices.
  - [ ] Implement Non-Negativity Constraints ($\tilde{y} \ge 0 \implies S \tilde{y}_b \ge 0$).
  - [ ] Implement bounded box constraints ($l \le S \tilde{y}_b \le u$).
  - [ ] Implement warm-starting logic using unconstrained solution $\tilde{y}_b^{unconstrained} = P \hat{y}$.
  - [ ] Add convergence validation and fallback strategy (e.g., clipping projected solution with iterative normalization).

### 2.4 Empirical Risk Minimization (ERM) & Probabilistic Reconciliation
- [ ] Implement `ERMReconciler`: Parameterized mapping operator $P_\theta$ optimized end-to-end to minimize explicit loss functions (MAE, MSE, CRPS) directly on coherent projections.
- [ ] Implement Probabilistic Reconciler (`SampleReconciler`):
  - [ ] Trajectory sample-based projection: Given base forecast samples $Y^{(s)} \in \mathbb{R}^{N \times S}$, compute coherent samples $\tilde{Y}^{(s)} = S P Y^{(s)}$.
  - [ ] Coherent Quantile Reconstruction via empirical distribution sorting and linear constraints solver.

### 2.5 High-Throughput Batch Processing Engine
- [ ] Implement `BatchReconciler` operating across multi-step horizon dimensions ($N \times H$).
- [ ] Support vectorized matrix multiplication $\tilde{Y} = S (P \hat{Y})$ avoiding per-step factorization overhead.
- [ ] Implement zero-copy buffer views for Pandas DataFrame and Polars DataFrame inputs/outputs.

---

### Definition of Done: Phase 2
- [ ] All reconciliation routines (OLS, WLS, MinT-Sample, MinT-Shrink, MinT-Diag, Top-Down, Bottom-Up, Middle-Out, Constrained QP) fully functional.
- [ ] Linear solver correctly falls back smoothly when encountering ill-conditioned matrices, logging appropriate diagnostic telemetry.
- [ ] Comprehensive unit tests confirm identity properties: $C \tilde{y} = \mathbf{0}$ for all coherent outputs within numerical precision $\epsilon \le 10^{-11}$.

---

## Phase 3: Automated Stress Testing & Verification (DoD Gates)

Subject the library to rigorous property-based testing, extreme edge cases, scale benchmarks, and numerical precision verification.

### 3.1 Mathematical & Property-Based Test Suite (`hypothesis`)
- [ ] Setup `hypothesis` strategies to generate arbitrary valid DAG hierarchies, grouped hierarchies, and continuous base forecast vectors.
- [ ] Test Invariant 1: **Coherence Invariant** — $\forall \hat{y}, \, C (S P \hat{y}) = \mathbf{0}$.
- [ ] Test Invariant 2: **Idempotency** — $P S = I_{n_b} \implies S P (S P \hat{y}) = S P \hat{y}$.
- [ ] Test Invariant 3: **Unbiasedness** — If base forecasts are unbiased ($E[\hat{y}] = y$), reconciled forecasts are unbiased ($E[\tilde{y}] = y$).
- [ ] Test Invariant 4: **Variance Reduction** — $\text{Tr}(\text{Var}(\tilde{y})) \le \text{Tr}(\text{Var}(\hat{y}))$ under MinT estimators.

### 3.2 Numerical Stability & Robustness Gates
- [ ] Edge Case Test: Near-singular matrix condition numbers ($\kappa(W) > 10^{12}$). Verify stabilization via diagonal jitter addition ($W_\epsilon = W + \epsilon I$).
- [ ] Edge Case Test: Hierarchies with extreme scale imbalances ($y_1 = 10^9, y_{100} = 10^{-6}$).
- [ ] Edge Case Test: Single-node hierarchy, multi-root graph structure, completely disconnected forest topologies.
- [ ] Edge Case Test: Zero-variance base series ($e_{i, t} = 0 \quad \forall t$).
- [ ] Non-negativity Gate: Verify zero constraint violations ($\tilde{y} \ge -10^{-9}$) across 1,000 randomized QP problem instances with negative base forecasts.

### 3.3 Scaling & Performance Benchmarks (`pytest-benchmark`)
- [ ] Implement standard execution benchmark suite evaluating time-to-solve and peak memory allocation across synthetic benchmarks:
  - [ ] Micro: $N = 100$ nodes, $n_b = 80$, $H = 24$.
  - [ ] Medium: $N = 5,000$ nodes, $n_b = 4,000$, $H = 52$.
  - [ ] Large: $N = 100,000$ nodes, $n_b = 85,000$, $H = 12$.
- [ ] Enforce SLA Performance Targets:
  - [ ] Medium scale unconstrained MinT projection (including sparse factorization) MUST execute in $< 250\text{ ms}$.
  - [ ] Sparse $P$ calculation for $N=100,000$ MUST maintain memory ceiling under $< 2.0\text{ GB}$ RSS.

---

### Definition of Done: Phase 3
- [ ] 100% pass rate on property-based test suite (minimum 5,000 examples per hypothesis test run).
- [ ] Zero failure rate across edge case matrix suites.
- [ ] Benchmark targets verified and enforced within GitHub Actions runner hardware limits.
- [ ] Test coverage $\ge 98\%$ enforced via `pytest-cov`.

---

## Phase 4: Packaging, Documentation & README

Assemble user-facing APIs, integration wrappers, reference documentation, and operational code examples.

### 4.1 Interface Integrations & Data Adapters
- [ ] Implement `PolarsAdapter`:
  - [ ] Native reconciliation mapping consuming `polars.DataFrame` or `polars.LazyFrame`.
  - [ ] Support zero-copy arrow bridge processing for structural series inputs.
- [ ] Implement `PandasAdapter`:
  - [ ] Support standard long-format DataFrames containing series key column, timestamp column, and base forecast value columns.
- [ ] Implement `StatsForecastAdapter` / `Nixtla` compatibility interface.

### 4.2 Comprehensive Documentation Suite
- [ ] Set up `mkdocs` with `mkdocs-material` theme, `pymdownx.arithmatex` (LaTeX support via MathJax), and `mkdocstrings`.
- [ ] Write Mathematical Formulation Guide:
  - [ ] Precise LaTeX exposition of Linear Projection methods ($P = (S^T W^{-1} S)^{-1} S^T W^{-1}$).
  - [ ] Structural variance vs. Empirical Covariance vs. Ledoit-Wolf Shrinkage derivations.
  - [ ] Non-negative quadratic programming bounds formulation.
- [ ] Produce End-to-End User Tutorials:
  - [ ] Tutorial 1: Cross-Sectional Tourism Hierarchical Forecasting.
  - [ ] Tutorial 2: Multi-Level Retail Product Grouping with Non-Negativity Constraints.
  - [ ] Tutorial 3: High-Scale Reconciler Integration with Polars DataFrames.
- [ ] Generate API Reference Documentation automatically from type hints and docstrings.

### 4.3 Production README & Asset Polish
- [ ] Draft high-impact `README.md`:
  - [ ] Project badge suite (CI status, PyPI version, Codecov coverage, Python versions, License).
  - [ ] Visual topology representation of hierarchical aggregation mapping.
  - [ ] Quick-start 10-second code snippet demonstrating core reconciliation loop.
  - [ ] Comprehensive benchmark matrix comparing speed/memory against native baseline implementations.
  - [ ] Architectural diagram explaining matrix projection steps.

---

### Definition of Done: Phase 4
- [ ] `mkdocs build` compiles cleanly with zero broken internal relative links or missing docstrings.
- [ ] Polars and Pandas adapters verified with full integration test coverage.
- [ ] Code snippets in `README.md` continuously validated via `phmdoctest` or `doctest`.

---

## Phase 5: Release & Production Readiness

Finalize automation workflows, security scans, semantic versioning controls, and release infrastructure.

### 5.1 Continuous Integration & Delivery (CI/CD)
- [ ] Finalize `.github/workflows/ci.yml`:
  - [ ] Multi-OS matrix testing (Ubuntu Latest, macOS Latest, Windows Latest).
  - [ ] Python matrix testing (3.11, 3.12, 3.13).
  - [ ] Automated execution of formatting (`ruff format --check`), linting (`ruff check`), type-checking (`mypy`), and test suite (`pytest`).
- [ ] Finalize `.github/workflows/publish.yml`:
  - [ ] Automated build triggering on semantic version tag push (`v*.*.*`).
  - [ ] PyPI publishing authentication using OpenID Connect (OIDC) trusted publisher tokenless authorization.
  - [ ] Automated release draft creation containing extracted release notes.

### 5.2 Security & Governance Infrastructure
- [ ] Add `SECURITY.md` defining vulnerability disclosure standards and reporting channels.
- [ ] Integrate static security analysis tool (`bandit -r src/`).
- [ ] Configure GitHub Dependency Review and Dependabot updates for setup actions and dev dependencies.
- [ ] Embed SLSA Provenance generation steps into build artifact release process.

### 5.3 Final Production Sign-Off Checklist
- [ ] Codebase audited for dead code, left-over dev comments, or `TODO` annotations.
- [ ] Package installability confirmed in isolated `venv` from built wheel (`pip install dist/*.whl`).
- [ ] `__all__` explicit module exports verified; zero leakage of private implementation modules.
- [ ] API stability frozen for Version `1.0.0` release tag.

---

### Definition of Done: Phase 5
- [ ] CI/CD pipelines green across all matrix targets.
- [ ] OpenID Connect PyPI trust established; verified via successful pre-release deploy to TestPyPI.
- [ ] Version `1.0.0` tagged, packaged, signed, and deployed.