import numpy as np
from scipy import linalg
from .models import ReconciliationRequest

class ReconciliationEngine:
    """
    Core engine for hierarchical reconciliation using MinT (Minimum Trace) logic.
    Implements: y_tilde = S * (S^T * W^-1 * S)^-1 * S^T * W^-1 * y_hat
    """

    @staticmethod
    def _get_covariance(residuals: np.ndarray, method: str) -> np.ndarray:
        n = residuals.shape[0]
        if method == "ols":
            return np.eye(n)
        
        if residuals.shape[1] <= 1:
            return np.eye(n)
            
        cov = np.cov(residuals)
        if method == "mint_sample":
            return cov
        
        if method == "mint_shrink":
            mu = np.mean(np.diag(cov))
            prior = mu * np.eye(n)
            delta = 0.1
            return (1 - delta) * cov + delta * prior
            
        return np.diag(np.diag(cov))

    def reconcile(self, request: ReconciliationRequest) -> np.ndarray:
        y_hat = np.array(request.forecasts)
        S = np.array(request.summation_matrix)
        
        # W is (n_series x n_series)
        W = self._get_covariance(y_hat, request.method)
        W_inv = linalg.pinv(W)
        
        # G = (S'W^-1S)^-1 S'W^-1
        # S.T is (n_bottom x n_series), W_inv is (n_series x n_series)
        # Result of S.T @ W_inv is (n_bottom x n_series)
        SW_inv = S.T @ W_inv
        inner = SW_inv @ S
        G = linalg.pinv(inner) @ SW_inv
        
        # Reconciled forecasts: S @ G @ y_hat
        y_tilde = S @ G @ y_hat
        return y_tilde

    async def process_async(self, request: ReconciliationRequest) -> np.ndarray:
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=1) as pool:
            return await loop.run_in_executor(pool, self.reconcile, request)