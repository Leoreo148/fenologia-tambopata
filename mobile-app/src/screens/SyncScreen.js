// Supabase Cloud Synchronization Screen
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  ActivityIndicator,
  Alert,
  ScrollView,
} from 'react-native';
import { getEstadisticasCampana } from '../database/queries';
import { sincronizarConNube } from '../services/supabaseClient';

export const SyncScreen = ({ navigation }) => {
  const [stats, setStats] = useState({ totalEvaluados: 0, pendientesSync: 0 });
  const [sincronizando, setSincronizando] = useState(false);
  const [ultimoMensaje, setUltimoMensaje] = useState(null);

  const cargarStats = async () => {
    const s = await getEstadisticasCampana();
    setStats(s);
  };

  useEffect(() => {
    cargarStats();
  }, []);

  const handleSync = async () => {
    setSincronizando(true);
    setUltimoMensaje(null);
    const res = await sincronizarConNube();
    setSincronizando(false);

    if (res.success) {
      setUltimoMensaje(res.message);
      await cargarStats();
      Alert.alert('✅ Sincronización Exitosa', res.message);
    } else {
      setUltimoMensaje(`⚠️ Nota: ${res.error || 'Servidor no accesible.'}`);
      Alert.alert('Estado de Red', res.error || 'Sin conexión con el servidor Supabase. Los datos permanecen 100% seguros en el almacenamiento local SQLite.');
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Text style={styles.backText}>❮ Volver</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Sincronización en la Nube</Text>
        <View style={{ width: 50 }} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>☁️ Base de Datos Supabase</Text>
          <Text style={styles.cardDesc}>
            Cuando llegues al albergue o a una zona con WiFi, presiona el botón para respaldar las evaluaciones de campo en la nube.
          </Text>

          <View style={styles.statusBox}>
            <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>Total Registros en el Celular:</Text>
              <Text style={styles.statusVal}>{stats.totalEvaluados}</Text>
            </View>
            <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>Pendientes de Subir:</Text>
              <Text style={[styles.statusVal, { color: stats.pendientesSync > 0 ? '#ea580c' : '#16a34a' }]}>
                {stats.pendientesSync}
              </Text>
            </View>
          </View>

          <TouchableOpacity
            style={[styles.syncBtn, sincronizando && styles.syncBtnDisabled]}
            onPress={handleSync}
            disabled={sincronizando}
          >
            {sincronizando ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <>
                <Text style={styles.syncBtnIcon}>🔄</Text>
                <Text style={styles.syncBtnText}>SUBIR EVALUACIONES A LA NUBE</Text>
              </>
            )}
          </TouchableOpacity>

          {ultimoMensaje && (
            <View style={styles.msgBox}>
              <Text style={styles.msgText}>{ultimoMensaje}</Text>
            </View>
          )}
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>🔒 Seguridad y Respaldo Total:</Text>
          <Text style={styles.infoText}>
            • Los datos se almacenan primero en SQLite local (no se pierden aunque se apague el celular).
            {'\n'}• El exportador CSV funciona de forma 100% independiente sin internet.
            {'\n'}• Cada registro cuenta con UUID único para evitar duplicados al sincronizar.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#f8fafc' },
  header: {
    backgroundColor: '#0f382c',
    paddingHorizontal: 14,
    paddingVertical: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  backBtn: { padding: 4 },
  backText: { color: '#81c784', fontWeight: '700', fontSize: 14 },
  headerTitle: { color: '#ffffff', fontSize: 16, fontWeight: '800' },
  content: { flex: 1, padding: 14 },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginBottom: 14,
  },
  cardTitle: { fontSize: 16, fontWeight: '900', color: '#0f172a', marginBottom: 6 },
  cardDesc: { fontSize: 12, color: '#64748b', lineHeight: 18, marginBottom: 14 },
  statusBox: {
    backgroundColor: '#f8fafc',
    borderRadius: 10,
    padding: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  statusRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  statusLabel: { fontSize: 13, color: '#475569', fontWeight: '600' },
  statusVal: { fontSize: 15, fontWeight: '900', color: '#0f172a' },
  syncBtn: {
    backgroundColor: '#0284c7',
    borderRadius: 12,
    paddingVertical: 14,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  syncBtnDisabled: { opacity: 0.6 },
  syncBtnIcon: { fontSize: 18, marginRight: 8 },
  syncBtnText: { color: '#ffffff', fontSize: 14, fontWeight: '900', letterSpacing: 0.5 },
  msgBox: {
    backgroundColor: '#eff6ff',
    borderRadius: 8,
    padding: 10,
    marginTop: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#3b82f6',
  },
  msgText: { fontSize: 12, color: '#1e40af', fontWeight: '600' },
  infoCard: {
    backgroundColor: '#f0fdf4',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#bbf7d0',
  },
  infoTitle: { fontSize: 13, fontWeight: '800', color: '#166534', marginBottom: 6 },
  infoText: { fontSize: 12, color: '#15803d', lineHeight: 18 },
});
