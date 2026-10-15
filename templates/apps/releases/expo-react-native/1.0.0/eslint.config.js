const { defineConfig } = require('eslint/config');
const expo = require('eslint-config-expo/flat');
module.exports = defineConfig([
  expo,
  {
    ignores: [
      '.gptclaw-cache/**',
      '.gptclaw-build/**',
      'coverage/**',
      '.cache/**',
      'checks/toolchain/**',
    ],
  },
]);
