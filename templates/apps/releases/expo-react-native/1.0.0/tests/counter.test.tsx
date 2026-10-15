import { render, screen, userEvent } from '@testing-library/react-native';
import { Counter } from '../src/components/Counter';

beforeEach(() => jest.useFakeTimers());
afterEach(() => {
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
});

test('increments and resets through accessible controls', async () => {
  const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
  await render(<Counter />);
  expect(screen.getByText('Count: 0')).toBeTruthy();
  await user.press(screen.getByRole('button', { name: 'Increase count' }));
  expect(screen.getByText('Count: 1')).toBeTruthy();
  await user.press(screen.getByRole('button', { name: 'Reset count' }));
  expect(screen.getByText('Count: 0')).toBeTruthy();
});
