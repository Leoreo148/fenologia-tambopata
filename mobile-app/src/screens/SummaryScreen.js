// Summary and CSV Export Screen (Official Macaw Society Nomenclature)
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { getEvaluacionesParaExportar } from '../database/queries';
import { exportarEvaluacionesCSV, generarNombreArchivo } from '../services/csvExporter';

export const SummaryScreen = ({ route, navigation }) => {
  const { parcela, fecha } = route.params || {};

  const [evaluaciones, setEvaluaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exportando, setExportando] = useState(false);

  useEffect(() => {
    const cargar = async () => {
      const pCod = parcela?.codigo || null;
      const fStr = fecha || null;
      const data = await getEvaluacionesParaExportar(pCod, fStr);
      setEvaluaciones(data);
      setLoading(false);
    };
    cargar();
  }, [parcela, fecha]);

  const handleExportarCSV = async () => {
    setExportando(true);
    const pCod = parcela?.codigo || null;
    const hab = parcela?.habitat || null;
    const fStr = fecha || null;

    const res = await exportarEvaluacionesCSV(pCod, fStr, hab);
    setExportando(false);

    if (res.success) {
      Alert.alert(
        '✅ Archivo CSV Generado',
        `Se ha generado el archivo oficial:\n\n📄 ${res.fileName}\n\nPuedes compartirlo por WhatsApp, Bluetooth o guardarlo en tu dispositivo.`,
        [{ text: 'Entendido' }]
      );
    } else {
      Alert.alert('Error', res.error || 'No se pudo exportar el archivo.');
    }
  };

  const nombreEsperado = generarNombreArchivo(
    parcela?.habitat || 'BOSQUE',
    parcela?.codigo || 'CAMPANA',
    new Date()
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Text style={styles.backText}>❮ Volver</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Resumen de Evaluaciones</Text>
        <View style={{ width: 50 }} />
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#1b5e20" />
          <Text style={{ marginTop: 10, color: '#64748b' }}>Cargando registros...</Text>
        </View>
      ) : (
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Tarjeta de Nomenclatura Oficial */}
          <View style={styles.nameCard}>
            <Text style={styles.nameCardTag}>NOMENCLATURA REGLAMENTARIA DE ARCHIVO</Text>
            <Text style={styles.nameCardTitle}>📄 {nombreEsperado}</Text>
            <Text style={styles.nameCardDesc}>
              Regla: [Hábitat] + [Parcela] + [Día/Mes/Año] compatible con Macaw Society
            </Text>
          </View>

          {/* Métricas del Lote */}
          <View style={styles.metricsRow}>
            <View style={styles.metricItem}>
              <Text style={styles.metricNumber}>{evaluaciones.length}</Text>
              <Text style={styles.metricLabel}>Registros</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricNumber}>
                {evaluaciones.filter(e => e.F > 0 || e.B > 0).length}
              </Text>
              <Text style={styles.metricLabel}>Con Flores</Text>
            </View>
            <View style={styles.metricItem}>
              <Text style={styles.metricNumber}>
                {evaluaciones.filter(e => e.FM > 0 || e.FV > 0).length}
              </Text>
              <Text style={styles.metricLabel}>Con Frutos</Text>
            </View>
          </View>

          {/* Botón Principal de Exportar CSV */}
          <TouchableOpacity
            style={styles.exportButton}
            activeOpacity={0.85}
            onPress={handleExportarCSV}
            disabled={exportando || evaluaciones.length === 0}
          >
            {exportando ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <>
                <Text style={styles.exportIcon}>📥</Text>
                <View>
                  <Text style={styles.exportTitle}>EXPORTAR Y COMPARTIR CSV</Text>
                  <Text style={styles.exportSub}>WhatsApp · Bluetooth · Guardar local</Text>
                </View>
              </>
            )}
          </TouchableOpacity>

          {/* Listado de Evaluaciones */}
          <Text style={styles.listHeader}>📑 DETALLE DE ÁRBOLES EVALUADOS ({evaluaciones.length}):</Text>
          {evaluaciones.length === 0 ? (
            <View style={styles.emptyBox}>
              <Text style={styles.emptyText}>No hay evaluaciones registradas aún.</Text>
            </View>
          ) : (
            evaluaciones.map((e, idx) => (
              <View key={idx} style={styles.evalCard}>
                <View style={styles.evalHeader}>
                  <Text style={styles.evalTag}>TAG {e.TAG}</Text>
                  <Text style={styles.evalPlop}>{e.PARCELA} (Sub {e.SUBPARCELA})</Text>
                </View>
                <Text style={styles.evalSp}>{e.NOMBRE_CIENTIFICO}</Text>
                <View style={styles.evalScores}>
                  <Text style={styles.scoreText}>B:{e.B} | F:{e.F} | FV:{e.FV} | FM:{e.FM} | D:{e.D}</Text>
                  <Text style={styles.vitalText}>{e.ESTADO_VITAL}</Text>
                </View>
              </View>
            ))
          )}

          <View style={{ height: 40 }} />
        </ScrollView>
      )}
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
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  nameCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1.5,
    borderColor: '#cbd5e1',
  },
  nameCardTag: { fontSize: 10, fontWeight: '800', color: '#15803d', letterSpacing: 0.5 },
  nameCardTitle: { fontSize: 17, fontWeight: '900', color: '#0f172a', marginVertical: 4 },
  nameCardDesc: { fontSize: 11, color: '#64748b' },
  metricsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  metricItem: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 10,
    padding: 12,
    alignItems: 'center',
    marginHorizontal: 3,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  metricNumber: { fontSize: 20, fontWeight: '900', color: '#0f382c' },
  metricLabel: { fontSize: 11, color: '#64748b', marginTop: 2 },
  exportButton: {
    backgroundColor: '#1b5e20',
    borderRadius: 14,
    paddingVertical: 16,
    paddingHorizontal: 18,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 4,
  },
  exportIcon: { fontSize: 24, marginRight: 12 },
  exportTitle: { fontSize: 15, fontWeight: '900', color: '#ffffff', letterSpacing: 0.5 },
  exportSub: { fontSize: 11, color: '#c8e6c9', marginTop: 2 },
  listHeader: { fontSize: 12, fontWeight: '800', color: '#475569', marginBottom: 8 },
  emptyBox: { backgroundColor: '#ffffff', padding: 20, borderRadius: 10, alignItems: 'center' },
  emptyText: { color: '#64748b', fontSize: 13 },
  evalCard: {
    backgroundColor: '#ffffff',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  evalHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 2 },
  evalTag: { fontSize: 14, fontWeight: '900', color: '#0f382c' },
  evalPlop: { fontSize: 12, fontWeight: '700', color: '#64748b' },
  evalSp: { fontSize: 13, fontStyle: 'italic', color: '#334155', marginBottom: 6 },
  evalScores: { flexDirection: 'row', justifyContent: 'space-between', borderTopWidth: 1, borderColor: '#f1f5f9', paddingTop: 6 },
  scoreText: { fontSize: 12, fontWeight: '800', color: '#2563eb' },
  vitalText: { fontSize: 11, fontWeight: '700', color: '#475569' },
});
