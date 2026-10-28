#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hstack_hook

raise SystemExit(hstack_hook.guard(sys.stdin.read()))
