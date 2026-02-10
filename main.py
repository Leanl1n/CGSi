"""Streamlit entry point. Run with: python main.py"""

import os
import subprocess
import sys


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(root, "src", "app.py")
    if not os.path.isfile(app_path):
        print(f"App not found: {app_path}", file=sys.stderr)
        return 1
    env = os.environ.copy()
    env["PYTHONPATH"] = root
    cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--", *sys.argv[1:]]
    try:
        result = subprocess.run(cmd, cwd=root, env=env)
        return result.returncode
    except FileNotFoundError:
        print(
            "Streamlit not found. Install with: pip install streamlit",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        print(f"Failed to run app: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
