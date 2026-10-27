const { jest: jestApi } = require('@jest/globals');
jestApi.mock('react-native-mmkv', () => ({
  createMMKV: () => {
    const values = new Map();
    return {
      set: (k, v) => values.set(k, v),
      getString: (k) => values.get(k),
      remove: (k) => values.delete(k),
    };
  },
}));
