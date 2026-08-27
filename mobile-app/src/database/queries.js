import { executeSql, querySql } from './db';

// Obtener todas las parcelas agrupadas
export const getParcelas = async () => {
  return await querySql('SELECT * FROM parcelas ORDER BY habitat, codigo ASC;');
};

// Obtener subparcelas de una parcela
export const getSubparcelas = async (plop) => {
  return await querySql(
    'SELECT DISTINCT sub FROM arboles WHERE plop = ? ORDER BY sub ASC;',
    [plop]
  );
};

// Obtener árboles de una parcela y subparcela específica (ordenados en secuencia de trocha)
export const getArbolesPorTrocha = async (plop, sub, fechaHoy = null) => {
  const sql = `
    SELECT 
      a.id, a.plop, a.sub, a.tag, a.nombre_cientifico, a.genero,
      e.boton, e.flor, e.fruto_verde, e.fruto_maduro, e.diseminado,
      e.estado_vital, e.notas, e.foto_uri, e.id as eval_id,
      CASE WHEN e.id IS NOT NULL THEN 1 ELSE 0 END as evaluado_hoy
    FROM arboles a
    LEFT JOIN evaluaciones e ON a.tag = e.tag AND a.plop = e.plop AND e.fecha = ?
    WHERE a.plop = ? AND a.sub = ?
    ORDER BY a.tag ASC;
  `;
  const dateStr = fechaHoy || new Date().toISOString().split('T')[0];
  return await querySql(sql, [dateStr, plop, sub]);
};

// Guardar o actualizar evaluación de un árbol
export const guardarEvaluacion = async (evalData) => {
  const id = evalData.id || `${evalData.plop}_${evalData.tag}_${evalData.fecha}`;
  const now = Date.now();

  const sql = `
    INSERT OR REPLACE INTO evaluaciones (
      id, tag, plop, sub, nombre_cientifico, fecha, mes, anio,
      boton, flor, fruto_verde, fruto_maduro, diseminado,
      estado_vital, notas, foto_uri, evaluador, sincronizado, timestamp_creacion
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
  `;

  await executeSql(sql, [
    id,
    evalData.tag,
    evalData.plop,
    evalData.sub,
    evalData.nombre_cientifico,
    evalData.fecha,
    evalData.mes,
    evalData.anio,
    evalData.boton || 0,
    evalData.flor || 0,
    evalData.fruto_verde || 0,
    evalData.fruto_maduro || 0,
    evalData.diseminado || 0,
    evalData.estado_vital || 'Normal',
    evalData.notas || '',
    evalData.foto_uri || '',
    evalData.evaluador || 'Investigador',
    0, // pendiente de sincronización
    now
  ]);

  return id;
};

// Obtener todas las evaluaciones para exportar CSV (de una parcela o de la campaña)
export const getEvaluacionesParaExportar = async (plop = null, fecha = null) => {
  let sql = `
    SELECT 
      e.id, e.plop as PARCELA, e.sub as SUBPARCELA, e.tag as TAG,
      e.nombre_cientifico as NOMBRE_CIENTIFICO, e.fecha as FECHA,
      e.mes as MES, e.anio as ANIO, e.boton as B, e.flor as F,
      e.fruto_verde as FV, e.fruto_maduro as FM, e.diseminado as D,
      e.estado_vital as ESTADO_VITAL, e.notas as NOTAS, e.evaluador as EVALUADOR,
      p.habitat as HABITAT, p.altura_msnm as ALTITUD, p.prefijo_nomenclatura as PREFIJO
    FROM evaluaciones e
    LEFT JOIN parcelas p ON e.plop = p.codigo
  `;
  const params = [];
  const conditions = [];

  if (plop) {
    conditions.push('e.plop = ?');
    params.push(plop);
  }
  if (fecha) {
    conditions.push('e.fecha = ?');
    params.push(fecha);
  }

  if (conditions.length > 0) {
    sql += ' WHERE ' + conditions.join(' AND ');
  }

  sql += ' ORDER BY e.plop, e.sub, e.tag ASC;';
  return await querySql(sql, params);
};

// Estadísticas generales de la campaña de 10 días
export const getEstadisticasCampana = async () => {
  const totalArboles = (await querySql('SELECT COUNT(*) as total FROM arboles;'))[0]?.total || 1939;
  const totalEvaluados = (await querySql('SELECT COUNT(DISTINCT tag) as total FROM evaluaciones;'))[0]?.total || 0;
  const pendientesSync = (await querySql('SELECT COUNT(*) as total FROM evaluaciones WHERE sincronizado = 0;'))[0]?.total || 0;

  return {
    totalArboles,
    totalEvaluados,
    pendientesSync,
    porcentajeProgreso: Math.round((totalEvaluados / totalArboles) * 100)
  };
};
