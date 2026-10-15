import { Link } from 'expo-router';
import { Image, StyleSheet, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Counter } from '../components/Counter';
export default function Home() {
  return (
    <SafeAreaView style={styles.screen}>
      <Image
        source={require('../../assets/icon.png')}
        accessibilityLabel="Native starter icon"
        style={{ width: 32, height: 32 }}
      />
      <Text accessibilityRole="header" style={styles.title}>
        Native app starter
      </Text>
      <Counter />
      <Link href="/about">About this starter</Link>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  screen: { flex: 1, padding: 24, gap: 24 },
  title: { fontSize: 24, fontWeight: '600' },
});
