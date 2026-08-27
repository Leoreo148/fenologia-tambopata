// Main Navigation Container for Macaw Society Fenología App
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import { SplashScreen } from './src/screens/SplashScreen';
import { HomeScreen } from './src/screens/HomeScreen';
import { ParcelSelector } from './src/screens/ParcelSelector';
import { FieldFormScreen } from './src/screens/FieldFormScreen';
import { SummaryScreen } from './src/screens/SummaryScreen';
import { SyncScreen } from './src/screens/SyncScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Splash"
        screenOptions={{
          headerShown: false,
          cardStyle: { backgroundColor: '#f8fafc' },
        }}
      >
        <Stack.Screen name="Splash" component={SplashScreen} />
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="ParcelSelector" component={ParcelSelector} />
        <Stack.Screen name="FieldForm" component={FieldFormScreen} />
        <Stack.Screen name="Summary" component={SummaryScreen} />
        <Stack.Screen name="Sync" component={SyncScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
