import unittest
import numpy as np
from src.hierarchical_forecast_reconciler.core import ReconciliationEngine
from src.hierarchical_forecast_reconciler.models import ReconciliationRequest

class TestReconciliationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ReconciliationEngine()
        # Simple 2-level hierarchy: Total = A + B
        self.S = [[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]]
        self.forecasts = [[100.0, 100.0], [45.0, 45.0], [55.0, 55.0]]

    def test_engine_initialization(self):
        """Verify engine instance creation."""
        self.assertIsInstance(self.engine, ReconciliationEngine)

    def test_ols_reconciliation_coherence(self):
        """Verify OLS reconciliation produces coherent results (Total = A + B)."""
        req = ReconciliationRequest(
            forecasts=self.forecasts,
            summation_matrix=self.S,
            method="ols"
        )
        result = self.engine.reconcile(req)
        # Check coherence: row 0 should equal row 1 + row 2
        np.testing.assert_allclose(result[0], result[1] + result[2], atol=1e-7)

    def test_mint_shrink_coherence(self):
        """Verify MinT Shrinkage produces coherent results."""
        req = ReconciliationRequest(
            forecasts=self.forecasts,
            summation_matrix=self.S,
            method="mint_shrink"
        )
        result = self.engine.reconcile(req)
        np.testing.assert_allclose(result[0], result[1] + result[2], atol=1e-7)

    def test_invalid_dimensions_validation(self):
        """Verify Pydantic validation catches empty matrices."""
        with self.assertRaises(ValueError):
            ReconciliationRequest(forecasts=[], summation_matrix=[])

    def test_covariance_ols_identity(self):
        """Verify OLS method returns identity matrix."""
        res = np.array([[1, 2], [3, 4]])
        cov = self.engine._get_covariance(res, "ols")
        np.testing.assert_array_equal(cov, np.eye(2))

    def test_mint_sample_covariance_calculation(self):
        """Verify MinT sample covariance matches numpy cov."""
        res = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        expected = np.cov(res)
        actual = self.engine._get_covariance(res, "mint_sample")
        np.testing.assert_allclose(actual, expected)

    def test_mint_shrink_positive_definiteness(self):
        """Verify shrinkage results in a positive definite matrix."""
        res = np.random.rand(3, 10)
        cov = self.engine._get_covariance(res, "mint_shrink")
        eigenvalues = np.linalg.eigvals(cov)
        self.assertTrue(np.all(eigenvalues > 0))

    def test_reconciliation_output_shape(self):
        """Verify output shape matches input shape."""
        req = ReconciliationRequest(
            forecasts=self.forecasts,
            summation_matrix=self.S,
            method="ols"
        )
        result = self.engine.reconcile(req)
        self.assertEqual(result.shape, (3, 2))

    def test_perfect_forecast_no_change(self):
        """If forecasts are already coherent, reconciliation should return them unchanged."""
        coherent_forecasts = [[100.0, 100.0], [50.0, 50.0], [50.0, 50.0]]
        req = ReconciliationRequest(
            forecasts=coherent_forecasts,
            summation_matrix=self.S,
            method="ols"
        )
        result = self.engine.reconcile(req)
        np.testing.assert_allclose(result, coherent_forecasts, atol=1e-7)

    def test_async_execution_wrapper(self):
        """Verify async wrapper returns correct values."""
        import asyncio
        req = ReconciliationRequest(
            forecasts=self.forecasts,
            summation_matrix=self.S,
            method="ols"
        )
        
        async def run_test():
            return await self.engine.process_async(req)
            
        result = asyncio.run(run_test())
        self.assertEqual(result.shape, (3, 2))

if __name__ == "__main__":
    unittest.main()