// Supabase Client and Batch Cloud Synchronizer
import { createClient } from '@supabase/supabase-js';
import { executeSql, querySql } from '../database/db';

// Configuración de Supabase (URL y Anon Key)
const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL || 'https://tambopata-macaw.supabase.co';
const SUPABASE_ANON_KEY = process.env.EXPO_PUBLIC_SUPABASE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_key';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/**
 * Sincroniza todas las evaluaciones pendientes locales hacia la nube
 */
export const sincronizarConNube = async () => {
  try {
    const pendientes = await querySql(
      'SELECT * FROM evaluaciones WHERE sincronizado = 0 ORDER BY timestamp_creacion ASC LIMIT 500;'
    );

    if (!pendientes || pendientes.length === 0) {
      return { success: true, count: 0, message: 'Todos los registros ya están sincronizados.' };
    }

    // Formatear para tabla de Supabase
    const payload = pendientes.map(p => ({
      id: p.id,
      tag: p.tag,
      plop: p.plop,
      sub: p.sub,
      nombre_cientifico: p.nombre_cientifico,
      fecha: p.fecha,
      mes: p.mes,
      anio: p.anio,
      boton: p.boton,
      flor: p.flor,
      fruto_verde: p.fruto_verde,
      fruto_maduro: p.fruto_maduro,
      diseminado: p.diseminado,
      estado_vital: p.estado_vital,
      notas: p.notas,
      evaluador: p.evaluador,
      foto_url: p.foto_uri,
      creado_en: new Date(p.timestamp_creacion).toISOString()
    }));

    // Intentar subida a Supabase
    const { data, error } = await supabase
      .from('evaluaciones_fenologicas')
      .upsert(payload, { onConflict: 'id' });

    if (error) {
      console.warn('Nota de sincronización: Servidor remoto pendiente de conexión:', error.message);
      // En modo local o prueba simulada, marcamos como sincronizados localmente si se desea
      return { success: false, count: 0, error: error.message };
    }

    // Marcar como sincronizados en SQLite
    const ids = pendientes.map(p => `'${p.id}'`).join(',');
    await executeSql(`UPDATE evaluaciones SET sincronizado = 1 WHERE id IN (${ids});`);

    return {
      success: true,
      count: pendientes.length,
      message: `¡Se sincronizaron ${pendientes.length} evaluaciones con éxito!`
    };
  } catch (error) {
    console.error('Error en sincronización Supabase:', error);
    return { success: false, count: 0, error: error.message };
  }
};
