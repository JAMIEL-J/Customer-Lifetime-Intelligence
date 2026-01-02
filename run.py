"""
run.py

Single entry point for the Customer Lifecycle Intelligence Platform.

Responsibilities:
- Validate runtime environment
- Trigger pipeline execution (optional warm start)
- Launch Streamlit dashboard

This file contains:
- NO business logic
- NO data transformations
- NO feature engineering
"""

import sys
import subprocess
from pathlib import Path


# =============================================================================
# CONFIGURATION
# =============================================================================

STREAMLIT_APP_PATH = "app.py"


# =============================================================================
# VALIDATION
# =============================================================================

def validate_environment() -> None:
    """Ensure required files exist before launch."""
    app_path = Path(STREAMLIT_APP_PATH)

    if not app_path.exists():
        raise FileNotFoundError(
            f"Streamlit app not found at: {STREAMLIT_APP_PATH}"
        )


# =============================================================================
# DASHBOARD LAUNCHER
# =============================================================================

def launch_dashboard() -> None:
    """Launch Streamlit dashboard."""
    print("=" * 60)
    print("Launching Customer Lifecycle Intelligence Dashboard")
    print("=" * 60)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            STREAMLIT_APP_PATH,
        ],
        check=True,
    )


# =============================================================================
# ENTRY POINT
# =============================================================================

def main() -> None:
    validate_environment()
    launch_dashboard()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
    except Exception as exc:
        print(f"\nStartup failed: {type(exc).__name__}: {exc}")
        sys.exit(1)
