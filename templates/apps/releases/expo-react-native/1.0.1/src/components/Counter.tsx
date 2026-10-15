import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

/** Small synthetic interaction used to verify the native starter. */
export function Counter() {
  const [count, setCount] = useState(0);
  return (
    <View style={styles.container}>
      <Text accessibilityLiveRegion="polite">Count: {count}</Text>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Increase count"
        onPress={() => setCount((value) => value + 1)}
        style={styles.button}
      >
        <Text>Increase count</Text>
      </Pressable>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Reset count"
        onPress={() => setCount(0)}
        style={styles.button}
      >
        <Text>Reset count</Text>
      </Pressable>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { gap: 16 },
  button: {
    minHeight: 48,
    justifyContent: 'center',
    padding: 16,
    backgroundColor: '#e5e7eb',
  },
});
