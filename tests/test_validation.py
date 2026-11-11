import unittest
from pydantic import ValidationError
from hierarchical_forecast_reconciler.models import ReconciliationRequest

class TestReconciliationValidation(unittest.TestCase):
    """
    Exhaustive validation suite for ReconciliationRequest schema enforcement.
    """

    def test_valid_request_schema(self):
        """Test that a well-formed request passes validation."""
        data = {
            "forecasts": [[10.0, 20.0], [5.0, 10.0]],
            "summation_matrix": [[1.0, 1.0]],
            "method": "ols"
        }
        request = ReconciliationRequest(**data)
        self.assertEqual(request.method, "ols")
        self.assertEqual(len(request.forecasts), 2)

    def test_empty_forecasts_matrix(self):
        """Test that empty matrix raises ValueError via field_validator."""
        data = {
            "forecasts": [],
            "summation_matrix": [[1.0]],
            "method": "mint_shrink"
        }
        with self.assertRaises(ValidationError):
            ReconciliationRequest(**data)

    def test_invalid_method_literal(self):
        """Test that unsupported reconciliation methods are rejected."""
        data = {
            "forecasts": [[1.0]],
            "summation_matrix": [[1.0]],
            "method": "invalid_method"
        }
        with self.assertRaises(ValidationError):
            ReconciliationRequest(**data)

    def test_missing_required_fields(self):
        """Test that missing mandatory fields raise ValidationError."""
        data = {"forecasts": [[1.0]]}
        with self.assertRaises(ValidationError):
            ReconciliationRequest(**data)

    def test_type_error_in_matrix(self):
        """Test that non-numeric types in matrix raise ValidationError."""
        data = {
            "forecasts": [["string_not_float"]],
            "summation_matrix": [[1.0]],
            "method": "ols"
        }
        with self.assertRaises(ValidationError):
            ReconciliationRequest(**data)

    def test_nested_empty_matrix(self):
        """Test that a matrix containing an empty list is rejected."""
        data = {
            "forecasts": [[]],
            "summation_matrix": [[1.0]],
            "method": "ols"
        }
        with self.assertRaises(ValidationError):
            ReconciliationRequest(**data)

    def test_default_method_assignment(self):
        """Test that the default method 'mint_shrink' is applied correctly."""
        data = {
            "forecasts": [[1.0]],
            "summation_matrix": [[1.0]]
        }
        request = ReconciliationRequest(**data)
        self.assertEqual(request.method, "mint_shrink")

    def test_summation_matrix_type_mismatch(self):
        """Test that passing a non-list for summation_matrix fails."""
        data = {
            "forecasts": [[1.0]],
            "summation_matrix": "not_a_list",
            "method": "ols"
        }
        with self.assertRaises(ValidationError):
            ReconciliationRequest(**data)

    def test_forecasts_as_flat_list_instead_of_matrix(self):
        """Test that a flat list instead of a list of lists fails."""
        data = {
            "forecasts": [1.0, 2.0],
            "summation_matrix": [[1.0]],
            "method": "ols"
        }
        # Pydantic will attempt to coerce, but if it fails to match List[List[float]], it raises
        with self.assertRaises(ValidationError):
            ReconciliationRequest(**data)

    def test_large_input_validation(self):
        """Test that large valid inputs are accepted without error."""
        data = {
            "forecasts": [[float(i) for i in range(100)] for _ in range(10)],
            "summation_matrix": [[1.0 for _ in range(10)]],
            "method": "mint_sample"
        }
        try:
            request = ReconciliationRequest(**data)
            self.assertEqual(len(request.forecasts), 10)
        except ValidationError:
            self.fail("ReconciliationRequest raised ValidationError unexpectedly!")

if __name__ == "__main__":
    unittest.main()