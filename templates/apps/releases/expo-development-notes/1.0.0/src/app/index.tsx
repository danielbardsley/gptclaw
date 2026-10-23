import { View } from 'react-native';
import { NativeProbe } from '../components/NativeProbe';
import { Notebook } from '../components/Notebook';

export default function App() {
  return (
    <View style={{ flex: 1 }}>
      <NativeProbe />
      <Notebook />
    </View>
  );
}
