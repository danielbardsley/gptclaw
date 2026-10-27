module.exports = {
  preset: 'jest-expo',
  testTimeout: 15000,
  testMatch: ['<rootDir>/tests/**/*.test.tsx'],
  collectCoverageFrom: ['src/components/**/*.tsx'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 },
  },
};
