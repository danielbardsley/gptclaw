#!/usr/bin/env python3
"""Git-only ephemeral fd authentication; no credential file/global lookup."""
import os
import sys
import re
from urllib.parse import urlsplit

if len(sys.argv) != 2:
    raise SystemExit(1)
match = re.search(r"'(https://[^']+)'", sys.argv[1])
if not match or urlsplit(match.group(1)).hostname != 'github.com' or urlsplit(match.group(1)).port is not None:
    raise SystemExit(1)
prompt = sys.argv[1].lower()
if 'username' in prompt:
    print('x-access-token')
elif 'password' in prompt:
    fd = int(os.environ['GPTCLAW_REPOSITORY_AUTH_FD'])
    sys.stdout.buffer.write(os.pread(fd, 16384, 0) + b'\n')
else:
    raise SystemExit(1)
