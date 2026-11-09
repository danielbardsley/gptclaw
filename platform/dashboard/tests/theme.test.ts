import assert from 'node:assert/strict';
import test from 'node:test';
import { runInNewContext } from 'node:vm';
import { themeBootstrap, validTheme } from '../lib/theme.ts';

function boot(saved: unknown, dark: boolean, blocked = false) {
  const dataset: Record<string, string> = {};
  runInNewContext(themeBootstrap, {
    document: { documentElement: { dataset } },
    window: { matchMedia: () => ({ matches: dark }) },
    localStorage: { getItem: () => { if (blocked) throw new Error('blocked'); return saved; } },
  });
  return dataset.theme;
}
test('explicit light and dark choices override the system before first paint', () => {
  for (const dark of [false, true]) {
    assert.equal(boot('light', dark), 'light');
    assert.equal(boot('dark', dark), 'dark');
  }
});
test('missing, invalid and inaccessible storage fall back to system theme', () => {
  for (const dark of [false, true]) {
    for (const saved of [null, '', 'auto', '<script>', undefined]) {
      assert.equal(boot(saved, dark), dark ? 'dark' : 'light');
    }
    assert.equal(boot(null, dark, true), dark ? 'dark' : 'light');
  }
});
test('only the two supported theme names can be persisted', () => {
  assert.ok(validTheme('dark')); assert.ok(validTheme('light'));
  for (const value of [null, undefined, {}, 'system', 'LIGHT']) assert.equal(validTheme(value), false);
});
