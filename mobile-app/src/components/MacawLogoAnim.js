// Animated Macaw Society Logo with flying macaws
import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Dimensions } from 'react-native';
import Svg, { Path, Circle, G } from 'react-native-svg';

const { width } = Dimensions.get('window');

export const MacawLogoAnim = ({ onAnimationComplete }) => {
  const leftMacawX = useRef(new Animated.Value(0)).current;
  const leftMacawY = useRef(new Animated.Value(0)).current;
  const rightMacawX = useRef(new Animated.Value(0)).current;
  const rightMacawY = useRef(new Animated.Value(0)).current;
  const logoScale = useRef(new Animated.Value(0.6)).current;
  const textOpacity = useRef(new Animated.Value(0)).current;
  const fadeOut = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Secuencia de animación fluida
    Animated.sequence([
      // 1. Entrada del logo y texto
      Animated.parallel([
        Animated.spring(logoScale, {
          toValue: 1,
          friction: 4,
          tension: 40,
          useNativeDriver: true,
        }),
        Animated.timing(textOpacity, {
          toValue: 1,
          duration: 900,
          useNativeDriver: true,
        }),
      ]),
      // 2. Vuelo de los guacamayos hacia los laterales
      Animated.parallel([
        Animated.timing(leftMacawX, {
          toValue: -width * 0.7,
          duration: 1200,
          useNativeDriver: true,
        }),
        Animated.timing(leftMacawY, {
          toValue: -150,
          duration: 1200,
          useNativeDriver: true,
        }),
        Animated.timing(rightMacawX, {
          toValue: width * 0.7,
          duration: 1200,
          useNativeDriver: true,
        }),
        Animated.timing(rightMacawY, {
          toValue: -150,
          duration: 1200,
          useNativeDriver: true,
        }),
      ]),
      // 3. Pausa breve y salida
      Animated.delay(400),
      Animated.timing(fadeOut, {
        toValue: 0,
        duration: 500,
        useNativeDriver: true,
      }),
    ]).start(() => {
      if (onAnimationComplete) {
        onAnimationComplete();
      }
    });
  }, []);

  return (
    <Animated.View style={[styles.container, { opacity: fadeOut }]}>
      {/* Guacamayo Izquierdo (Ara macao - Escarlata) */}
      <Animated.View
        style={[
          styles.macawWrapper,
          {
            transform: [
              { translateX: leftMacawX },
              { translateY: leftMacawY },
              { rotate: '-25deg' },
            ],
          },
        ]}
      >
        <Svg width="70" height="70" viewBox="0 0 100 100">
          <G>
            {/* Cuerpo y alas rojas / amarillas / azules */}
            <Path d="M10 50 Q30 20 60 40 T90 50 Q70 70 40 60 Z" fill="#e74c3c" />
            <Path d="M25 45 Q45 25 65 40 T85 45" fill="#f1c40f" />
            <Path d="M40 50 Q60 30 75 45 T85 50" fill="#2980b9" />
            {/* Cola larga escarlata */}
            <Path d="M15 50 Q5 75 0 95 Q10 80 25 55 Z" fill="#c0392b" />
            <Circle cx="80" cy="42" r="3" fill="#ffffff" />
            <Circle cx="81" cy="42" r="1.5" fill="#000000" />
            <Path d="M85 43 Q95 45 92 52 Q87 49 84 46 Z" fill="#ffffff" stroke="#2c3e50" strokeWidth="1" />
          </G>
        </Svg>
      </Animated.View>

      {/* Isotipo Central de The Macaw Society */}
      <Animated.View style={[styles.centerLogo, { transform: [{ scale: logoScale }] }]}>
        <View style={styles.badgeCircle}>
          <Text style={styles.badgeEmoji}>🦜</Text>
        </View>
        <Animated.View style={{ opacity: textOpacity, alignItems: 'center' }}>
          <Text style={styles.brandTitle}>THE MACAW SOCIETY</Text>
          <Text style={styles.brandSubtitle}>Fenología Tambopata · 2026</Text>
          <View style={styles.divider} />
          <Text style={styles.locationText}>Reserva Nacional Tambopata · Madre de Dios</Text>
        </Animated.View>
      </Animated.View>

      {/* Guacamayo Derecho (Ara ararauna - Azul y Amarillo) */}
      <Animated.View
        style={[
          styles.macawWrapper,
          {
            transform: [
              { translateX: rightMacawX },
              { translateY: rightMacawY },
              { rotate: '25deg' },
            ],
          },
        ]}
      >
        <Svg width="70" height="70" viewBox="0 0 100 100">
          <G transform="scale(-1, 1) translate(-100, 0)">
            <Path d="M10 50 Q30 20 60 40 T90 50 Q70 70 40 60 Z" fill="#2980b9" />
            <Path d="M25 45 Q45 25 65 40 T85 45" fill="#f39c12" />
            <Path d="M15 50 Q5 75 0 95 Q10 80 25 55 Z" fill="#1f618d" />
            <Circle cx="80" cy="42" r="3" fill="#ffffff" />
            <Circle cx="81" cy="42" r="1.5" fill="#000000" />
            <Path d="M85 43 Q95 45 92 52 Q87 49 84 46 Z" fill="#ffffff" stroke="#2c3e50" strokeWidth="1" />
          </G>
        </Svg>
      </Animated.View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: '#0d2b1d', // Verde selva profundo
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 999,
  },
  macawWrapper: {
    position: 'absolute',
    top: '38%',
  },
  centerLogo: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  badgeCircle: {
    width: 110,
    height: 110,
    borderRadius: 55,
    backgroundColor: '#1b5e20',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    borderWidth: 3,
    borderColor: '#4caf50',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 10,
    elevation: 10,
  },
  badgeEmoji: {
    fontSize: 54,
  },
  brandTitle: {
    color: '#ffffff',
    fontSize: 24,
    fontWeight: '900',
    letterSpacing: 2,
    textAlign: 'center',
  },
  brandSubtitle: {
    color: '#81c784',
    fontSize: 16,
    fontWeight: '600',
    marginTop: 6,
    letterSpacing: 1,
    textAlign: 'center',
  },
  divider: {
    width: 60,
    height: 3,
    backgroundColor: '#f1c40f',
    marginVertical: 14,
    borderRadius: 2,
  },
  locationText: {
    color: '#a5d6a7',
    fontSize: 12,
    fontWeight: '400',
    textAlign: 'center',
  },
});
