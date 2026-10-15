module.exports = {
  preset: 'jest-expo',
  testTimeout: 30000,
  testMatch: ['<rootDir>/tests/**/*.test.tsx'],
  collectCoverageFrom: ['src/components/**/*.tsx', 'src/api/client.ts'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 },
  },
};
