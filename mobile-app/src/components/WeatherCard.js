// Multi-source weather ensemble card for the field home screen
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export const WeatherCard = ({ forecast }) => {
  if (!forecast) return null;

  const { hoy, manana, recomendacion, ventanaOptima, online } = forecast;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.badgeRow}>
          <Text style={styles.title}>🌤️ Clima Cuadrante Tambopata</Text>
          <View style={[styles.statusDot, { backgroundColor: online ? '#4caf50' : '#ffa000' }]} />
          <Text style={styles.statusText}>{online ? 'En vivo' : 'Caché'}</Text>
        </View>
        <Text style={styles.subtitle}>Ensamble ECMWF + GFS + FLDAS</Text>
      </View>

      <View style={styles.metricsRow}>
        {/* Hoy */}
        <View style={styles.dayBox}>
          <Text style={styles.dayTitle}>HOY</Text>
          <Text style={styles.tempText}>{hoy.tempMax}° / {hoy.tempMin}°C</Text>
          <Text style={styles.rainText}>🌧️ {hoy.probLluvia}% ({hoy.precipitacionMm} mm)</Text>
          <Text style={styles.humText}>💧 Humedad: {hoy.humedadRelativa}%</Text>
        </View>

        {/* Mañana */}
        <View style={[styles.dayBox, styles.dayBoxHighlight]}>
          <Text style={[styles.dayTitle, { color: '#1b5e20' }]}>MAÑANA (CAMPAÑA)</Text>
          <Text style={styles.tempText}>{manana.tempMax}° / {manana.tempMin}°C</Text>
          <Text style={[styles.rainText, { color: manana.probLluvia > 60 ? '#c62828' : '#2e7d32' }]}>
            🌧️ {manana.probLluvia}% ({manana.precipitacionMm} mm)
          </Text>
          <Text style={styles.humText}>Ventana: {ventanaOptima}</Text>
        </View>
      </View>

      {/* Recomendación de salida a campo */}
      <View style={styles.recBox}>
        <Text style={styles.recText}>{recomendacion}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 14,
    marginVertical: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  header: {
    marginBottom: 10,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  title: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0f172a',
    flex: 1,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 4,
  },
  statusText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#64748b',
  },
  subtitle: {
    fontSize: 11,
    color: '#64748b',
    marginTop: 2,
  },
  metricsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  dayBox: {
    flex: 1,
    backgroundColor: '#f8fafc',
    borderRadius: 10,
    padding: 10,
    marginRight: 6,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  dayBoxHighlight: {
    marginRight: 0,
    marginLeft: 6,
    backgroundColor: '#f0fdf4',
    borderColor: '#bbf7d0',
  },
  dayTitle: {
    fontSize: 11,
    fontWeight: '800',
    color: '#475569',
    marginBottom: 4,
  },
  tempText: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0f172a',
    marginBottom: 2,
  },
  rainText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#2563eb',
    marginBottom: 2,
  },
  humText: {
    fontSize: 11,
    color: '#64748b',
  },
  recBox: {
    backgroundColor: '#eff6ff',
    borderRadius: 8,
    padding: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#3b82f6',
  },
  recText: {
    fontSize: 12,
    color: '#1e40af',
    fontWeight: '600',
  },
});
