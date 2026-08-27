// Splash Screen
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { MacawLogoAnim } from '../components/MacawLogoAnim';

export const SplashScreen = ({ navigation }) => {
  const handleFinish = () => {
    navigation.replace('Home');
  };

  return (
    <View style={styles.container}>
      <MacawLogoAnim onAnimationComplete={handleFinish} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d2b1d',
  },
});
