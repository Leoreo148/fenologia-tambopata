// CSV Exporter with Official Macaw Society Nomenclature
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { Platform } from 'react-native';
import { getEvaluacionesParaExportar } from '../database/queries';

/**
 * Genera el nombre reglamentario del archivo:
 * Formato: [PREFIJO_HABITAT][CODIGO_PARCELA]_[DDMMAA].csv
 * Ejemplo: BBFP1_281226.csv (Bosque Bajío, Parcela FP1, 28 de Diciembre 2026)
 */
export const generarNombreArchivo = (habitat, parcelaCodigo, fechaObj = new Date()) => {
  const prefijos = {
    'BOSQUE DE BAJÍO': 'BB',
    'BOSQUE DE BAJIO': 'BB',
    'BOSQUE DE TIERRA FIRME': 'BTF',
    'BOSQUE DE AGUAJAL': 'BAG',
    'BOSQUE SUCESIONAL': 'BS'
  };

  const pref = prefijos[(habitat || '').toUpperCase()] || 'B';
  const dia = String(fechaObj.getDate()).padStart(2, '0');
  const mes = String(fechaObj.getMonth() + 1).padStart(2, '0');
  const anio = String(fechaObj.getFullYear()).slice(-2);

  return `${pref}${parcelaCodigo}_${dia}${mes}${anio}.csv`;
};

/**
 * Exporta las evaluaciones a CSV y abre el diálogo nativo para compartir
 */
export const exportarEvaluacionesCSV = async (parcelaCodigo = null, fecha = null, habitat = null) => {
  try {
    const rows = await getEvaluacionesParaExportar(parcelaCodigo, fecha);

    if (!rows || rows.length === 0) {
      throw new Error('No hay evaluaciones registradas para exportar.');
    }

    // Cabecera compatible con el protocolo histórico Macaw Society
    const headers = [
      'PARCELA',
      'SUBPARCELA',
      'TAG',
      'HABITAT',
      'ALTITUD_MSNM',
      'NOMBRE_CIENTIFICO',
      'FECHA',
      'MES',
      'ANIO',
      'BOTON',
      'FLOR',
      'FRUTO_VERDE',
      'FRUTO_MADURO',
      'DISEMINADO',
      'ESTADO_VITAL',
      'NOTAS',
      'EVALUADOR'
    ];

    const csvLines = [headers.join(',')];

    for (const r of rows) {
      const line = [
        `"${r.PARCELA || ''}"`,
        `"${r.SUBPARCELA || ''}"`,
        r.TAG || '',
        `"${r.HABITAT || ''}"`,
        r.ALTITUD || '',
        `"${r.NOMBRE_CIENTIFICO || ''}"`,
        `"${r.FECHA || ''}"`,
        r.MES || '',
        r.ANIO || '',
        r.B ?? 0,
        r.F ?? 0,
        r.FV ?? 0,
        r.FM ?? 0,
        r.D ?? 0,
        `"${r.ESTADO_VITAL || 'Normal'}"`,
        `"${(r.NOTAS || '').replace(/"/g, '""')}"`,
        `"${r.EVALUADOR || ''}"`
      ];
      csvLines.push(line.join(','));
    }

    const csvContent = csvLines.join('\n');
    const fileName = generarNombreArchivo(
      habitat || rows[0]?.HABITAT,
      parcelaCodigo || rows[0]?.PARCELA || 'CAMPANA',
      new Date()
    );

    // En navegador Web (fallback)
    if (Platform.OS === 'web') {
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      return { success: true, fileName, uri: url };
    }

    // En Android / iOS
    const fileUri = `${FileSystem.documentDirectory}${fileName}`;
    await FileSystem.writeAsStringAsync(fileUri, csvContent, {
      encoding: FileSystem.EncodingType.UTF8
    });

    if (await Sharing.isAvailableAsync()) {
      await Sharing.shareAsync(fileUri, {
        mimeType: 'text/csv',
        dialogTitle: `Compartir Respaldo Fenológico ${fileName}`,
        UTI: 'public.comma-separated-values-text'
      });
    }

    return { success: true, fileName, fileUri };
  } catch (error) {
    console.error('Error exportando CSV:', error);
    return { success: false, error: error.message };
  }
};
