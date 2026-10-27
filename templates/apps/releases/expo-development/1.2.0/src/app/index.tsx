import { Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeProbe } from '../components/NativeProbe';

export default function Home() {
  return (
    <SafeAreaView style={{ flex: 1, padding: 24, gap: 24 }}>
      <Text accessibilityRole="header">Android development client</Text>
      <NativeProbe />
    </SafeAreaView>
  );
}
