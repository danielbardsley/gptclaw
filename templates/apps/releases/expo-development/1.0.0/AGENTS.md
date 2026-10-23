# Native development project guidance

Read the product spec/design/tasks and preserve unrelated changes. Use the exact
SDK-57 development profile and frozen Node/pnpm tools. Run managed verify; build
exports JS/assets, while native-build submits only with explicit configured scope.
Use generated-native ownership; do not commit or overwrite hand-edited android/ios
source. Keep app configuration static and public, and all credentials outside source.
Do not install host packages, expose public Metro or submit stores/updates.
