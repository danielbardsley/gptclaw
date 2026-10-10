#!/usr/bin/env python3
"""CI-only synthetic template generation; tool/dependency execution stays in Docker."""
from pathlib import Path
import sys
import os
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app

base=Path(sys.argv[1]).absolute()
base.mkdir(mode=0o700)
app.PROJECTS=base
app.STORE=base/'.gptclaw-runtime/v1'
print(app.create('template-ci',template='nextjs',template_version='1.0.0')['root'])
