FROM mcr.microsoft.com/playwright@sha256:bc72a8df40831ded821e3cbc79c318c21b44d6e51dff9fd89ace7a8249c5b462
COPY playwright.tgz /tmp/playwright.tgz
RUN mkdir -p /checks/node_modules/playwright-core && tar xzf /tmp/playwright.tgz -C /checks/node_modules/playwright-core --strip-components=1 && rm /tmp/playwright.tgz
WORKDIR /checks
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
