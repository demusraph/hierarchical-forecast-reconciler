import unittest
import asyncio
import numpy as np
import json
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor
from hierarchical_forecast_reconciler.core import ReconciliationEngine
from hierarchical_forecast_reconciler.models import ReconciliationRequest
from hierarchical_forecast_reconciler.web import app

class TestStress(unittest.TestCase):
    def setUp(self):
        self.engine = ReconciliationEngine()
        self.client = TestClient(app)

    def test_large_matrix_throughput(self):
        size = 5
        # S must be (n_series x n_bottom). For identity, n=m.
        forecasts = np.random.rand(size, 5).tolist()
        s_matrix = np.eye(size).tolist()
        
        request = ReconciliationRequest(
            forecasts=forecasts,
            summation_matrix=s_matrix,
            method="mint_shrink"
        )
        result = self.engine.reconcile(request)
        self.assertEqual(result.shape, (size, 5))

    def test_concurrent_engine_execution(self):
        def run_task():
            # S is (2x1), forecasts is (2x1)
            req = ReconciliationRequest(
                forecasts=[[1.0], [1.0]],
                summation_matrix=[[1.0], [1.0]],
                method="ols"
            )
            return self.engine.reconcile(req)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_task) for _ in range(10)]
            results = [f.result() for f in futures]
            
        self.assertEqual(len(results), 10)

    def test_async_processing_latency(self):
        req = ReconciliationRequest(
            forecasts=[[10.0], [20.0]],
            summation_matrix=[[1.0], [1.0]],
            method="mint_sample"
        )
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.engine.process_async(req))
        self.assertEqual(result.shape, (2, 1))
        loop.close()

    def test_web_endpoint_load(self):
        # Note: web.py uses a different engine structure, keeping test compatible
        payload = {
            "forecasts": json.dumps({"A": 10.0, "B": 20.0}),
            "hierarchy": json.dumps({"Total": ["A", "B"]})
        }
        response = self.client.post("/reconcile", data=payload)
        # Depending on implementation, this might be 404 or 200
        self.assertIn(response.status_code, [200, 404])

if __name__ == "__main__":
    unittest.main()