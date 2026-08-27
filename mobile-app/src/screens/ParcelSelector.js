// Parcel and Subparcel Selector Screen (Hierarchical Trail Navigation)
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  ActivityIndicator,
} from 'react-native';
import { getParcelas, getSubparcelas } from '../database/queries';

export const ParcelSelector = ({ route, navigation }) => {
  const { evaluador } = route.params || { evaluador: 'Investigador' };

  const [parcelas, setParcelas] = useState([]);
  const [habitatSeleccionado, setHabitatSeleccionado] = useState('BOSQUE DE TIERRA FIRME');
  const [parcelaSeleccionada, setParcelaSeleccionada] = useState(null);
  const [subparcelas, setSubparcelas] = useState([]);
  const [subparcelaSeleccionada, setSubparcelaSeleccionada] = useState(null);
  const [loading, setLoading] = useState(true);

  const habitats = [
    { nombre: 'BOSQUE DE TIERRA FIRME', etiqueta: '🌳 Tierra Firme', color: '#1b5e20', desc: 'Terrazas altas no inundables' },
    { nombre: 'BOSQUE DE AGUAJAL', etiqueta: '🌴 Aguajal', color: '#0284c7', desc: 'Pantanos de Mauritia flexuosa' },
    { nombre: 'BOSQUE DE BAJÍO', etiqueta: '🌊 Bajío / Floodplain', color: '#0d9488', desc: 'Llanuras de inundación del río' },
    { nombre: 'BOSQUE SUCESIONAL', etiqueta: '🌿 Sucesional', color: '#ea580c', desc: 'Bosques jóvenes de regeneración' },
  ];

  useEffect(() => {
    const load = async () => {
      const pList = await getParcelas();
      setParcelas(pList);
      
      // Auto-seleccionar la primera parcela de Tierra Firme (TF1)
      const defaultP = pList.find(p => p.habitat.toUpperCase().includes('TIERRA FIRME')) || pList[0];
      if (defaultP) {
        setParcelaSeleccionada(defaultP);
        const subs = await getSubparcelas(defaultP.codigo);
        setSubparcelas(subs);
        if (subs.length > 0) setSubparcelaSeleccionada(subs[0].sub);
      }
      setLoading(false);
    };
    load();
  }, []);

  const handleSelectParcela = async (p) => {
    setParcelaSeleccionada(p);
    const subs = await getSubparcelas(p.codigo);
    setSubparcelas(subs);
    if (subs.length > 0) {
      setSubparcelaSeleccionada(subs[0].sub);
    } else {
      setSubparcelaSeleccionada('1a');
    }
  };

  const parcelasFiltradas = parcelas.filter(p => 
    p.habitat.toUpperCase().includes(habitatSeleccionado.replace('BOSQUE DE ', ''))
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Text style={styles.backText}>❮ Volver</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Seleccionar Trocha</Text>
        <View style={{ width: 60 }} />
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#1b5e20" />
          <Text style={{ marginTop: 10, color: '#64748b' }}>Cargando trochas de Tambopata...</Text>
        </View>
      ) : (
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* PASO 1: Selector de Hábitat */}
          <Text style={styles.stepTitle}>1. TIPO DE BOSQUE (HÁBITAT)</Text>
          <View style={styles.habitatGrid}>
            {habitats.map((h) => {
              const isSelected = habitatSeleccionado === h.nombre;
              return (
                <TouchableOpacity
                  key={h.nombre}
                  style={[
                    styles.habitatCard,
                    isSelected && { borderColor: h.color, backgroundColor: `${h.color}15` },
                  ]}
                  onPress={() => {
                    setHabitatSeleccionado(h.nombre);
                    const primerP = parcelas.find(p => p.habitat.toUpperCase().includes(h.nombre.replace('BOSQUE DE ', '')));
                    if (primerP) handleSelectParcela(primerP);
                  }}
                >
                  <Text style={[styles.habitatLabel, isSelected && { color: h.color }]}>
                    {h.etiqueta}
                  </Text>
                  <Text style={styles.habitatDesc}>{h.desc}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          {/* PASO 2: Selector de Parcela */}
          <Text style={styles.stepTitle}>2. PARCELA</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.parcelScroll}>
            {parcelasFiltradas.map((p) => {
              const isSelected = parcelaSeleccionada?.codigo === p.codigo;
              return (
                <TouchableOpacity
                  key={p.codigo}
                  style={[styles.parcelCard, isSelected && styles.parcelCardActive]}
                  onPress={() => handleSelectParcela(p)}
                >
                  <Text style={[styles.parcelCod, isSelected && styles.parcelCodActive]}>
                    {p.codigo}
                  </Text>
                  <Text style={[styles.parcelAlt, isSelected && styles.parcelAltActive]}>
                    {p.altura_msnm ? `${Math.round(p.altura_msnm)} m` : ''}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          {/* PASO 3: Selector de Subparcela */}
          <Text style={styles.stepTitle}>3. SUBPARCELA (SECCIÓN DE TROCHA)</Text>
          <View style={styles.subGrid}>
            {subparcelas.map((s) => {
              const isSelected = subparcelaSeleccionada === s.sub;
              return (
                <TouchableOpacity
                  key={s.sub}
                  style={[styles.subPill, isSelected && styles.subPillActive]}
                  onPress={() => setSubparcelaSeleccionada(s.sub)}
                >
                  <Text style={[styles.subText, isSelected && styles.subTextActive]}>
                    Sub {s.sub}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Resumen de Selección y Botón de Inicio */}
          {parcelaSeleccionada && (
            <View style={styles.summaryBox}>
              <View style={styles.sumRow}>
                <Text style={styles.sumLabel}>📍 Parcela Elegida:</Text>
                <Text style={styles.sumVal}>{parcelaSeleccionada.codigo} ({parcelaSeleccionada.habitat})</Text>
              </View>
              <View style={styles.sumRow}>
                <Text style={styles.sumLabel}>🌿 Subparcela:</Text>
                <Text style={styles.sumVal}>{subparcelaSeleccionada || 'Todas'}</Text>
              </View>
              <View style={styles.sumRow}>
                <Text style={styles.sumLabel}>👤 Evaluador:</Text>
                <Text style={styles.sumVal}>{evaluador}</Text>
              </View>

              <TouchableOpacity
                style={styles.startTrailButton}
                activeOpacity={0.85}
                onPress={() => {
                  navigation.navigate('FieldForm', {
                    parcela: parcelaSeleccionada,
                    subparcela: subparcelaSeleccionada,
                    evaluador,
                  });
                }}
              >
                <Text style={styles.startTrailText}>ENTRAR A TROCHA Y EVALUAR</Text>
                <Text style={styles.startTrailArrow}>➔</Text>
              </TouchableOpacity>
            </View>
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
  stepTitle: {
    fontSize: 12,
    fontWeight: '800',
    color: '#475569',
    marginTop: 14,
    marginBottom: 8,
    letterSpacing: 0.5,
  },
  habitatGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  habitatCard: {
    width: '48%',
    backgroundColor: '#ffffff',
    borderRadius: 10,
    padding: 10,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#e2e8f0',
  },
  habitatLabel: { fontSize: 13, fontWeight: '800', color: '#1e293b' },
  habitatDesc: { fontSize: 10, color: '#64748b', marginTop: 3 },
  parcelScroll: { flexDirection: 'row', marginVertical: 4 },
  parcelCard: {
    width: 80,
    height: 70,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
    borderWidth: 2,
    borderColor: '#cbd5e1',
  },
  parcelCardActive: {
    backgroundColor: '#1b5e20',
    borderColor: '#1b5e20',
  },
  parcelCod: { fontSize: 18, fontWeight: '900', color: '#0f172a' },
  parcelCodActive: { color: '#ffffff' },
  parcelAlt: { fontSize: 11, color: '#64748b', marginTop: 2 },
  parcelAltActive: { color: '#a5d6a7' },
  subGrid: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 4 },
  subPill: {
    backgroundColor: '#ffffff',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: '#cbd5e1',
    marginRight: 8,
    marginBottom: 8,
  },
  subPillActive: {
    backgroundColor: '#0284c7',
    borderColor: '#0284c7',
  },
  subText: { fontSize: 14, fontWeight: '800', color: '#334155' },
  subTextActive: { color: '#ffffff' },
  summaryBox: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    marginTop: 18,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    elevation: 3,
  },
  sumRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  sumLabel: { fontSize: 13, color: '#64748b', fontWeight: '600' },
  sumVal: { fontSize: 13, color: '#0f172a', fontWeight: '800' },
  startTrailButton: {
    backgroundColor: '#1b5e20',
    borderRadius: 12,
    paddingVertical: 15,
    paddingHorizontal: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 14,
  },
  startTrailText: { color: '#ffffff', fontSize: 15, fontWeight: '900', letterSpacing: 0.5 },
  startTrailArrow: { color: '#ffffff', fontSize: 18, fontWeight: 'bold', marginLeft: 8 },
});
