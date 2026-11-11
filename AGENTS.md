# AGENTS.md: Hierarchical Forecast Reconciler (HFR)

## 1. Project Overview & Core Mission
The **Hierarchical Forecast Reconciler (HFR)** is a high-performance engine designed to enforce mathematical consistency across multi-level time-series hierarchies (e.g., SKU -> Category -> Region). 

**Core Mission:** Implement MinT (Minimum Trace) and Bottom-Up reconciliation algorithms with O(n) complexity, ensuring that aggregated forecasts satisfy the summation constraints of the hierarchy. The system must maintain strict numerical stability for large-scale enterprise datasets.

---

## 2. Local PowerShell Commands
All operations must be executed from the project root.

*   **Setup:** `python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -r requirements.txt`
*   **Test:** `pytest tests/ --cov=hfr --cov-report=term-missing --durations=10`
*   **Run:** `python -m hfr.cli --config ./configs/prod.yaml --input ./data/raw.csv`
*   **Lint:** `ruff check . && mypy hfr/ --strict && black --check .`
*   **Clean:** `Get-ChildItem -Path . -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force`

---

## 3. Engineering Invariants
*   **Zero-Placeholder Mandate:** No `TODO`, `FIXME`, or `pass` statements allowed in production code. Every branch must be implemented or explicitly raised as `NotImplementedError` with a tracking issue ID.
*   **Typing Strictness:** All signatures must use `mypy --strict` compliance. Use `typing.Protocol` for dependency injection and `Final` for immutable configuration constants.
*   **CRLF/LF Preservation:** The repository enforces `LF` line endings. Ensure `.gitattributes` is respected.
*   **Memory Safety:** Large matrices must be handled via `numpy` memory mapping or `pandas` chunking. No loading of >1GB datasets into raw Python lists.
*   **Modularity:** Logic must be decoupled into `core/` (math), `io/` (data ingestion), and `api/` (reconciliation interface).

---

## 4. Self-Healing & Error Recovery Protocol
When an agent encounters a runtime failure:

1.  **Traceback Analysis:**
    *   Capture the full stack trace.
    *   Identify if the error is a `DimensionalityMismatch` (matrix alignment) or `NumericalInstability` (singular matrix).
2.  **Local Inspection:**
    *   Use `breakpoint()` in the failing module.
    *   Verify the shape of the reconciliation matrix $S$ and the forecast vector $\hat{y}$ using `assert` statements.
3.  **Correction Loop:**
    *   If a matrix is singular, implement Tikhonov regularization ($\lambda I$).
    *   If performance degrades, profile using `cProfile` and optimize the bottleneck (typically the matrix inversion step).
4.  **Verification:**
    *   Run the specific unit test that triggered the failure.
    *   Ensure the fix does not violate existing constraints in `tests/test_constraints.py`.

---

## 5. Definition of Done (DoD) Quality Gate
A task is considered "Done" only when the following conditions are met:

*   **Coverage:** 100% branch coverage for new logic.
*   **Static Analysis:** Zero errors reported by `mypy --strict` and `ruff`.
*   **Performance:** Reconciliation of a 10k-node hierarchy completes in < 500ms on standard CI hardware.
*   **Documentation:** Every public function/class has a Google-style docstring including `Args`, `Returns`, and `Raises` sections.
*   **Integration:** The feature is successfully integrated into the `main` branch via a clean PR, passing all CI/CD pipeline stages.
*   **Mathematical Proof:** For new algorithms, a markdown-based proof of constraint satisfaction is included in `docs/math/`.