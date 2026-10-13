import { Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
export default function About() {
  return (
    <SafeAreaView>
      <Text>
        This synthetic React Native starter uses Expo and TypeScript. Backend
        integration and managed device access are separate features.
      </Text>
    </SafeAreaView>
  );
}
