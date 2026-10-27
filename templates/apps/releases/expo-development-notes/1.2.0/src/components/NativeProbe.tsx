import { useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { nativeRoundTrip } from '../native-demo';

export function NativeProbe() {
  const [result, setResult] = useState('Not checked');
  return (
    <View>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Check native storage"
        style={{ minHeight: 48, justifyContent: 'center', padding: 12 }}
        onPress={() => {
          try {
            setResult(
              nativeRoundTrip()
                ? 'Native storage passed'
                : 'Native storage failed',
            );
          } catch {
            setResult('Native storage failed');
          }
        }}
      >
        <Text>Check native storage</Text>
      </Pressable>
      <Text accessibilityLiveRegion="polite">{result}</Text>
    </View>
  );
}
