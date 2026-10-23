import { fireEvent, render } from '@testing-library/react-native';
import { NativeProbe } from '../src/components/NativeProbe';
import * as demo from '../src/native-demo';

afterEach(() => jest.restoreAllMocks());

test('native storage probe reports the round trip', async () => {
  const screen = await render(<NativeProbe />);
  await fireEvent.press(screen.getByLabelText('Check native storage'));
  expect(screen.getByText('Native storage passed')).toBeTruthy();
});

test.each(['false', 'throw'])('native failure %s is visible', async (mode) => {
  jest.spyOn(demo, 'nativeRoundTrip').mockImplementation(() => {
    if (mode === 'throw')
      throw new Error('Synthetic unavailable native module');
    return false;
  });
  const screen = await render(<NativeProbe />);
  await fireEvent.press(screen.getByLabelText('Check native storage'));
  expect(screen.getByText('Native storage failed')).toBeTruthy();
});
