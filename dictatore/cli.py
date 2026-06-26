from __future__ import annotations

import os
import sys

from dictatore.doctor import run as run_doctor


def dispatch() -> None:
    if len(sys.argv) < 2:
        print("Usage: dictatore <command>", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "doctor":
        results = run_doctor()
        for line in results:
            print(line)
        errors = [r for r in results if "not found" in r.lower() or "not installed" in r.lower()]
        if errors:
            sys.exit(1)

    elif command == "models":
        from pathlib import Path
        models_dir = Path.home() / ".local" / "share" / "dictatore" / "models"
        if models_dir.is_dir():
            for entry in sorted(models_dir.iterdir()):
                if entry.is_dir():
                    print(entry.name)
        else:
            print("No models directory found", file=sys.stderr)

    elif command == "config":
        from dictatore.config import CONFIG_DIR, DEFAULT_CONFIG
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_path = CONFIG_DIR / "config.py"

        if not config_path.exists():
            lines = [
                "# Dictatore configuration",
                "# Uncomment and change any value below.",
                "",
            ]
            for key, val in DEFAULT_CONFIG.items():
                if isinstance(val, str):
                    lines.append(f'# {key} = "{val}"')
                elif isinstance(val, bool):
                    lines.append(f"# {key} = {str(val)}")
                else:
                    lines.append(f"# {key} = {val}")
            lines.append("")
            lines.append("# Optional text transform:")
            lines.append("# def transform(text):")
            lines.append("#     return text.replace(\"linux\", \"Linux\")")
            config_path.write_text("\n".join(lines) + "\n")

        import subprocess
        for editor in ("$EDITOR", "xdg-open", "nano", "vim"):
            ed = editor if not editor.startswith("$") else os.environ.get(editor[1:])
            if ed:
                subprocess.run([ed, str(config_path)], check=False)
                return

    elif command == "install":
        print("Interactive installer not yet implemented")
        print("See README.md for manual setup instructions")

    elif command == "daemon":
        from dictatore.daemon import start_daemon
        start_daemon()

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Commands: doctor, models, config, install, daemon", file=sys.stderr)
        sys.exit(1)
