import json
from pathlib import Path

from main import app


def export_openapi():
    output_path = Path(__file__).resolve().parent / "openapi.json"

    output_path.write_text(
        json.dumps(app.openapi(), indent=2),
        encoding="utf-8",
    )

    print(f"OpenAPI specification saved to: {output_path}")


if __name__ == "__main__":
    export_openapi()