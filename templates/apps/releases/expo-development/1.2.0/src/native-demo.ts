import { createMMKV } from 'react-native-mmkv';

export function nativeRoundTrip(): boolean {
  const store = createMMKV({ id: 'gptclaw-synthetic-native-check' });
  store.set('probe', 'native-ok');
  const passed = store.getString('probe') === 'native-ok';
  store.remove('probe');
  return passed;
}
