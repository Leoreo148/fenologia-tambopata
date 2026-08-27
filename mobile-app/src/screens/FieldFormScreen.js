// Field Evaluation Screen (Trail Sequence with High-Contrast Score Bars)
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  TextInput,
  Alert,
} from 'react-native';
import { PhenoScoreBar } from '../components/PhenoScoreBar';
import { getArbolesPorTrocha, guardarEvaluacion } from '../database/queries';

export const FieldFormScreen = ({ route, navigation }) => {
  const { parcela, subparcela, evaluador } = route.params;

  const [arboles, setArboles] = useState([]);
  const [indiceActual, setIndiceActual] = useState(0);
  const [fechaHoy] = useState(new Date().toISOString().split('T')[0]);

  // Estado del árbol actual en pantalla
  const [boton, setBoton] = useState(0);
  const [flor, setFlor] = useState(0);
  const [frutoVerde, setFrutoVerde] = useState(0);
  const [frutoMaduro, setFrutoMaduro] = useState(0);
  const [diseminado, setDiseminado] = useState(0);
  const [estadoVital, setEstadoVital] = useState('Normal');
  const [notas, setNotas] = useState('');
  const [guardadoFeedback, setGuardadoFeedback] = useState(false);

  useEffect(() => {
    const cargar = async () => {
      const lista = await getArbolesPorTrocha(parcela.codigo, subparcela, fechaHoy);
      setArboles(lista);
      if (lista.length > 0) {
        cargarValoresArbol(lista[0]);
      }
    };
    cargar();
  }, [parcela, subparcela]);

  const cargarValoresArbol = (arbol) => {
    setBoton(arbol.boton || 0);
    setFlor(arbol.flor || 0);
    setFrutoVerde(arbol.fruto_verde || 0);
    setFrutoMaduro(arbol.fruto_maduro || 0);
    setDiseminado(arbol.diseminado || 0);
    setEstadoVital(arbol.estado_vital || 'Normal');
    setNotas(arbol.notas || '');
  };

  const guardarActual = async () => {
    if (arboles.length === 0) return;
    const currentTree = arboles[indiceActual];
    const ahora = new Date();

    const evalData = {
      tag: currentTree.tag,
      plop: parcela.codigo,
      sub: subparcela,
      nombre_cientifico: currentTree.nombre_cientifico,
      fecha: fechaHoy,
      mes: ahora.getMonth() + 1,
      anio: ahora.getFullYear(),
      boton,
      flor,
      fruto_verde: frutoVerde,
      fruto_maduro: frutoMaduro,
      diseminado,
      estado_vital: estadoVital,
      notas,
      evaluador,
    };

    await guardarEvaluacion(evalData);

    // Actualizar estado local
    const copia = [...arboles];
    copia[indiceActual] = { ...copia[indiceActual], ...evalData, evaluado_hoy: 1 };
    setArboles(copia);

    setGuardadoFeedback(true);
    setTimeout(() => setGuardadoFeedback(false), 1200);
  };

  const handleSiguiente = async () => {
    await guardarActual();
    if (indiceActual < arboles.length - 1) {
      const proxIndice = indiceActual + 1;
      setIndiceActual(proxIndice);
      cargarValoresArbol(arboles[proxIndice]);
    } else {
      Alert.alert(
        '🎉 ¡Subparcela Completada!',
        `Has registrado los ${arboles.length} árboles de la subparcela ${subparcela}.`,
        [
          { text: 'Quedarse aquí', style: 'cancel' },
          { text: 'Ver Resumen y Exportar', onPress: () => navigation.navigate('Summary', { parcela, fecha: fechaHoy }) },
        ]
      );
    }
  };

  const handleAnterior = async () => {
    await guardarActual();
    if (indiceActual > 0) {
      const prevIndice = indiceActual - 1;
      setIndiceActual(prevIndice);
      cargarValoresArbol(arboles[prevIndice]);
    }
  };

  const arbolActual = arboles[indiceActual] || {};
  const evaluadosCount = arboles.filter(a => a.evaluado_hoy === 1).length;
  const progresoPorcentaje = arboles.length > 0 ? Math.round((evaluadosCount / arboles.length) * 100) : 0;

  const estadosVitales = ['Normal', 'Desramado', 'Caído / Muerto', 'Nuevo'];

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Barra de Trocha y Progreso Superior */}
      <View style={styles.topBar}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Text style={styles.backText}>❮ Trocha</Text>
        </TouchableOpacity>
        <View style={styles.trailInfo}>
          <Text style={styles.trailTitle}>{parcela.codigo} · Sub {subparcela}</Text>
          <Text style={styles.trailProgress}>
            Árbol {indiceActual + 1} de {arboles.length} ({progresoPorcentaje}%)
          </Text>
        </View>
        <TouchableOpacity
          onPress={() => navigation.navigate('Summary', { parcela, fecha: fechaHoy })}
          style={styles.summaryTopBtn}
        >
          <Text style={styles.summaryTopBtnText}>Resumen</Text>
        </TouchableOpacity>
      </View>

      {/* Barra visual de progreso */}
      <View style={styles.progressBarBg}>
        <View style={[styles.progressBarFill, { width: `${progresoPorcentaje}%` }]} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Tarjeta de Identificación del Árbol (TAG) */}
        <View style={styles.treeCard}>
          <View style={styles.tagHeader}>
            <View style={styles.tagBadge}>
              <Text style={styles.tagLabel}>PLACA / TAG</Text>
              <Text style={styles.tagNumber}>{arbolActual.tag || '---'}</Text>
            </View>
            <View style={styles.treeMeta}>
              <Text style={styles.spName}>{arbolActual.nombre_cientifico || 'Cargando...'}</Text>
              <Text style={styles.habitatMeta}>{parcela.habitat} · {parcela.altura_msnm}m</Text>
            </View>
          </View>
        </View>

        {/* 1. Selector de Estado Vital */}
        <View style={styles.vitalSection}>
          <Text style={styles.sectionHeader}>🌱 ESTADO VITAL DEL INDIVIDUO:</Text>
          <View style={styles.vitalPillsRow}>
            {estadosVitales.map((ev) => {
              const isSelected = estadoVital === ev;
              let btnColor = '#1b5e20';
              if (ev === 'Caído / Muerto') btnColor = '#dc2626';
              if (ev === 'Desramado') btnColor = '#d97706';
              if (ev === 'Nuevo') btnColor = '#7c3aed';

              return (
                <TouchableOpacity
                  key={ev}
                  style={[
                    styles.vitalPill,
                    isSelected && { backgroundColor: btnColor, borderColor: btnColor },
                  ]}
                  onPress={() => setEstadoVital(ev)}
                >
                  <Text style={[styles.vitalText, isSelected && { color: '#ffffff' }]}>
                    {ev}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {/* 2. Escalas Fenológicas (Botones Táctiles 0 a 4) */}
        <View style={styles.phenoBox}>
          <PhenoScoreBar
            icon="🌱"
            label="Botones Florales (B)"
            value={boton}
            onChange={setBoton}
            color="#16a34a"
          />
          <PhenoScoreBar
            icon="🌸"
            label="Flores Abiertas (F)"
            value={flor}
            onChange={setFlor}
            color="#2563eb"
          />
          <PhenoScoreBar
            icon="🍏"
            label="Frutos Verdes / Inmaduros (FV)"
            value={frutoVerde}
            onChange={setFrutoVerde}
            color="#059669"
          />
          <PhenoScoreBar
            icon="🍎"
            label="Frutos Maduros (FM)"
            value={frutoMaduro}
            onChange={setFrutoMaduro}
            color="#ea580c"
          />
          <PhenoScoreBar
            icon="🍂"
            label="Diseminado / Caído (D)"
            value={diseminado}
            onChange={setDiseminado}
            color="#9333ea"
          />
        </View>

        {/* 3. Notas y Observaciones */}
        <View style={styles.notesBox}>
          <Text style={styles.sectionHeader}>📝 NOTAS / OBSERVACIONES DE CAMPO:</Text>
          <TextInput
            style={styles.notesInput}
            placeholder="Lianas en copa, ataque de insectos, etc."
            placeholderTextColor="#94a3b8"
            value={notas}
            onChangeText={setNotas}
            multiline
          />
        </View>

        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Barra Inferior Fija de Navegación de Trocha */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={[styles.navBtn, indiceActual === 0 && styles.navBtnDisabled]}
          onPress={handleAnterior}
          disabled={indiceActual === 0}
        >
          <Text style={styles.navBtnText}>❮ Anterior</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navBtn, styles.saveBtn]}
          onPress={guardarActual}
        >
          <Text style={styles.saveBtnText}>
            {guardadoFeedback ? '✓ Guardado' : '💾 Guardar'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navBtn, styles.nextBtn]}
          onPress={handleSiguiente}
        >
          <Text style={styles.nextBtnText}>
            {indiceActual === arboles.length - 1 ? 'Finalizar 🏁' : 'Siguiente ❯'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#f1f5f9' },
  topBar: {
    backgroundColor: '#0f382c',
    paddingHorizontal: 12,
    paddingVertical: 10,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  backBtn: { padding: 4 },
  backText: { color: '#81c784', fontWeight: '700', fontSize: 13 },
  trailInfo: { alignItems: 'center' },
  trailTitle: { color: '#ffffff', fontSize: 16, fontWeight: '900' },
  trailProgress: { color: '#a5d6a7', fontSize: 11, fontWeight: '600', marginTop: 1 },
  summaryTopBtn: { backgroundColor: '#1b5e20', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  summaryTopBtnText: { color: '#ffffff', fontSize: 11, fontWeight: '800' },
  progressBarBg: { height: 4, backgroundColor: '#cbd5e1' },
  progressBarFill: { height: '100%', backgroundColor: '#16a34a' },
  content: { flex: 1, padding: 12 },
  treeCard: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1.5,
    borderColor: '#cbd5e1',
    elevation: 2,
  },
  tagHeader: { flexDirection: 'row', alignItems: 'center' },
  tagBadge: {
    backgroundColor: '#0f382c',
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 12,
    alignItems: 'center',
    marginRight: 12,
  },
  tagLabel: { fontSize: 9, fontWeight: '800', color: '#81c784', letterSpacing: 0.5 },
  tagNumber: { fontSize: 22, fontWeight: '900', color: '#ffffff' },
  treeMeta: { flex: 1 },
  spName: { fontSize: 16, fontWeight: '800', color: '#0f172a', fontStyle: 'italic' },
  habitatMeta: { fontSize: 11, color: '#64748b', marginTop: 3 },
  vitalSection: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  sectionHeader: { fontSize: 11, fontWeight: '800', color: '#475569', marginBottom: 8 },
  vitalPillsRow: { flexDirection: 'row', flexWrap: 'wrap' },
  vitalPill: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1.5,
    borderColor: '#cbd5e1',
    backgroundColor: '#f8fafc',
    marginRight: 6,
    marginBottom: 4,
  },
  vitalText: { fontSize: 12, fontWeight: '700', color: '#334155' },
  phenoBox: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  notesBox: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  notesInput: {
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    padding: 10,
    fontSize: 13,
    color: '#0f172a',
    borderWidth: 1,
    borderColor: '#cbd5e1',
    minHeight: 50,
  },
  bottomNav: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#ffffff',
    paddingHorizontal: 12,
    paddingVertical: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderColor: '#e2e8f0',
    elevation: 8,
  },
  navBtn: {
    flex: 1,
    height: 48,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f1f5f9',
    marginHorizontal: 3,
    borderWidth: 1,
    borderColor: '#cbd5e1',
  },
  navBtnDisabled: { opacity: 0.4 },
  navBtnText: { fontSize: 13, fontWeight: '800', color: '#334155' },
  saveBtn: { backgroundColor: '#f0fdf4', borderColor: '#86efac' },
  saveBtnText: { fontSize: 13, fontWeight: '800', color: '#15803d' },
  nextBtn: { backgroundColor: '#1b5e20', borderColor: '#1b5e20', flex: 1.2 },
  nextBtnText: { fontSize: 14, fontWeight: '900', color: '#ffffff' },
});
