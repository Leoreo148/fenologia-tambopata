// Home Screen: Profile Selector + Weather + Quick Launch
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import { WeatherCard } from '../components/WeatherCard';
import { getPronosticoRegional } from '../services/weatherService';
import { getEstadisticasCampana } from '../database/queries';
import { initDatabase } from '../database/db';

export const HomeScreen = ({ navigation }) => {
  const [evaluador, setEvaluador] = useState('👨‍🌾 Tío (Investigador Principal)');
  const [forecast, setForecast] = useState(null);
  const [stats, setStats] = useState({ totalArboles: 1939, totalEvaluados: 0, pendientesSync: 0, porcentajeProgreso: 0 });
  const [dbReady, setDbReady] = useState(false);

  const perfiles = [
    '👨‍🌾 Tío (Investigador Principal)',
    '👩‍🔬 Tesista 1 (Fenología)',
    '👩‍🔬 Tesista 2 (Dispersión)',
    '🌿 Guardaparque / Asistente',
  ];

  useEffect(() => {
    const setup = async () => {
      await initDatabase();
      setDbReady(true);
      const st = await getEstadisticasCampana();
      setStats(st);
      const fc = await getPronosticoRegional();
      setForecast(fc);
    };
    setup();
  }, []);

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor="#0f382c" />
      
      {/* Header Principal */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>THE MACAW SOCIETY</Text>
          <Text style={styles.headerSubtitle}>Fenología Tambopata · Campaña 10 Días</Text>
        </View>
        <View style={styles.badgeOnline}>
          <Text style={styles.badgeText}>OFFLINE OK</Text>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Selector de Perfil (Sin contraseñas) */}
        <View style={styles.profileSection}>
          <Text style={styles.sectionLabel}>👤 EVALUADOR ACTIVO:</Text>
          <View style={styles.profilesGrid}>
            {perfiles.map((p) => {
              const isSelected = evaluador === p;
              return (
                <TouchableOpacity
                  key={p}
                  style={[styles.profilePill, isSelected && styles.profilePillActive]}
                  onPress={() => setEvaluador(p)}
                >
                  <Text style={[styles.profileText, isSelected && styles.profileTextActive]}>
                    {p}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {/* Pronóstico Meteorológico Ensamble */}
        <WeatherCard forecast={forecast} />

        {/* Progreso de la Campaña de 10 días */}
        <View style={styles.statsCard}>
          <Text style={styles.statsTitle}>📊 Estado de la Campaña Actual</Text>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{stats.totalEvaluados}</Text>
              <Text style={styles.statLabel}>Evaluados</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{stats.totalArboles}</Text>
              <Text style={styles.statLabel}>Total Árboles</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{stats.porcentajeProgreso}%</Text>
              <Text style={styles.statLabel}>Completado</Text>
            </View>
          </View>
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: `${Math.min(stats.porcentajeProgreso, 100)}%` }]} />
          </View>
        </View>

        {/* Botones de Acción Primaria */}
        <TouchableOpacity
          style={styles.mainButton}
          activeOpacity={0.85}
          onPress={() => navigation.navigate('ParcelSelector', { evaluador })}
        >
          <Text style={styles.mainButtonIcon}>🧭</Text>
          <View style={styles.mainButtonTextWrapper}>
            <Text style={styles.mainButtonTitle}>IR A CAMPO / EVALUAR TROCHA</Text>
            <Text style={styles.mainButtonSubtitle}>Seleccionar Parcela y Subparcela</Text>
          </View>
          <Text style={styles.mainButtonArrow}>➔</Text>
        </TouchableOpacity>

        <View style={styles.secondaryButtonsRow}>
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => navigation.navigate('Summary')}
          >
            <Text style={styles.secBtnIcon}>📥</Text>
            <Text style={styles.secBtnText}>Exportar CSV</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => navigation.navigate('Sync')}
          >
            <Text style={styles.secBtnIcon}>☁️</Text>
            <Text style={styles.secBtnText}>Sync Supabase</Text>
          </TouchableOpacity>
        </View>

        <View style={{ height: 30 }} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    backgroundColor: '#0f382c',
    paddingHorizontal: 16,
    paddingVertical: 18,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '900',
    color: '#ffffff',
    letterSpacing: 1,
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#81c784',
    marginTop: 2,
  },
  badgeOnline: {
    backgroundColor: '#1b5e20',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#4caf50',
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#ffffff',
  },
  content: {
    flex: 1,
    paddingHorizontal: 14,
  },
  profileSection: {
    marginTop: 12,
    marginBottom: 6,
  },
  sectionLabel: {
    fontSize: 11,
    fontWeight: '800',
    color: '#475569',
    marginBottom: 6,
  },
  profilesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  profilePill: {
    backgroundColor: '#ffffff',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1.5,
    borderColor: '#cbd5e1',
    marginRight: 6,
    marginBottom: 6,
  },
  profilePillActive: {
    backgroundColor: '#0f382c',
    borderColor: '#0f382c',
  },
  profileText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },
  profileTextActive: {
    color: '#ffffff',
  },
  statsCard: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 14,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    elevation: 2,
  },
  statsTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 10,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 10,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: '900',
    color: '#1b5e20',
  },
  statLabel: {
    fontSize: 11,
    color: '#64748b',
    marginTop: 2,
  },
  progressBarBg: {
    height: 8,
    backgroundColor: '#e2e8f0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#16a34a',
    borderRadius: 4,
  },
  mainButton: {
    backgroundColor: '#1b5e20',
    borderRadius: 14,
    paddingVertical: 16,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 5,
  },
  mainButtonIcon: {
    fontSize: 28,
    marginRight: 12,
  },
  mainButtonTextWrapper: {
    flex: 1,
  },
  mainButtonTitle: {
    fontSize: 15,
    fontWeight: '900',
    color: '#ffffff',
    letterSpacing: 0.5,
  },
  mainButtonSubtitle: {
    fontSize: 12,
    color: '#c8e6c9',
    marginTop: 2,
  },
  mainButtonArrow: {
    fontSize: 20,
    color: '#ffffff',
    fontWeight: 'bold',
  },
  secondaryButtonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  secBtnIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  secBtnText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#1e293b',
  },
});
