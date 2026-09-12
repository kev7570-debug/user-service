import json
from pathlib import Path

from app.main import create_app


def test_required_openapi_operations_and_responses_are_present():
    reference_path = Path(__file__).parents[2] / "docs" / "kefir_python_junior_test.json"
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    actual = create_app(init_database=False).openapi()

    for path, methods in reference["paths"].items():
        for method, operation in methods.items():
            assert method in actual["paths"][path]
            expected_codes = set(operation.get("responses", {}))
            actual_codes = set(actual["paths"][path][method].get("responses", {}))
            assert expected_codes <= actual_codes
