# Native source architecture

Expo Router resolves native screens under src/app. Shared components use React
Native primitives; tests live outside route discovery. The app has no hosted API,
database or authentication. Add them through the product spec and reviewed mobile
backend binding rather than bundling DB credentials. Static app.json holds public
development identity; continuous native generation is the ownership model, with
native source and signed builds deferred to reviewed follow-ups. Platform job state
lives outside this checkout. The starter's examples are intentional synthetic data.
