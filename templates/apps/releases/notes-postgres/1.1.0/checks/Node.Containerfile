FROM docker.io/library/node@sha256:51b1100cc2a83d370c6a60952e3f2989c8a43159d0e38586e090f3b3326efefd
COPY install-pnpm.cjs /tmp/install-pnpm.cjs
COPY node-profile.json /tmp/profile.json
RUN node /tmp/install-pnpm.cjs && rm /tmp/install-pnpm.cjs /tmp/profile.json
ENV NEXT_TELEMETRY_DISABLED=1 PNPM_HOME=/tmp/pnpm XDG_CACHE_HOME=/tmp/pnpm-cache XDG_CONFIG_HOME=/tmp/pnpm-config XDG_STATE_HOME=/tmp/pnpm-state
WORKDIR /workspace
