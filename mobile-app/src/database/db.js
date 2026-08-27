// Database manager for 100% Offline SQLite storage
import * as SQLite from 'expo-sqlite';
import seedData from './seedData.json';

let db = null;

export const initDatabase = async () => {
  try {
    if (SQLite.openDatabaseSync) {
      db = SQLite.openDatabaseSync('tambopata_fenologia.db');
    } else {
      db = SQLite.openDatabase('tambopata_fenologia.db');
    }

    // 1. Crear tabla de parcelas
    await executeSql(`
      CREATE TABLE IF NOT EXISTS parcelas (
        codigo TEXT PRIMARY KEY,
        habitat TEXT,
        este_utm REAL,
        norte_utm REAL,
        altura_msnm REAL,
        latitud REAL,
        longitud REAL,
        prefijo_nomenclatura TEXT
      );
    `);

    // 2. Crear tabla de árboles (1,939 árboles del censo)
    await executeSql(`
      CREATE TABLE IF NOT EXISTS arboles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plop TEXT,
        sub TEXT,
        tag INTEGER,
        nombre_cientifico TEXT,
        genero TEXT,
        estado_vital TEXT DEFAULT 'Normal'
      );
    `);

    // 3. Crear tabla de evaluaciones fenológicas de campo
    await executeSql(`
      CREATE TABLE IF NOT EXISTS evaluaciones (
        id TEXT PRIMARY KEY,
        tag INTEGER,
        plop TEXT,
        sub TEXT,
        nombre_cientifico TEXT,
        fecha TEXT,
        mes INTEGER,
        anio INTEGER,
        boton INTEGER DEFAULT 0,
        flor INTEGER DEFAULT 0,
        fruto_verde INTEGER DEFAULT 0,
        fruto_maduro INTEGER DEFAULT 0,
        diseminado INTEGER DEFAULT 0,
        estado_vital TEXT DEFAULT 'Normal',
        notas TEXT,
        foto_uri TEXT,
        evaluador TEXT,
        sincronizado INTEGER DEFAULT 0,
        timestamp_creacion INTEGER
      );
    `);

    // Verificar si ya se sembró el censo
    const countResult = await querySql('SELECT COUNT(*) as count FROM arboles;');
    const count = countResult[0]?.count || 0;

    if (count === 0) {
      console.log('Sembrando censo maestro en SQLite (1,939 árboles y 25 parcelas)...');
      
      // Insertar parcelas
      for (const p of seedData.parcelas) {
        await executeSql(
          `INSERT OR REPLACE INTO parcelas (codigo, habitat, este_utm, norte_utm, altura_msnm, latitud, longitud, prefijo_nomenclatura)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?);`,
          [p.CODIGO, p.HABITAT, p.ESTE_UTM19L, p.NORTE_UTM19L, p.ALTURA_MSNM, p.LATITUD, p.LONGITUD, p.prefijo_nomenclatura]
        );
      }

      // Insertar árboles
      for (const a of seedData.arboles) {
        await executeSql(
          `INSERT INTO arboles (plop, sub, tag, nombre_cientifico, genero, estado_vital)
           VALUES (?, ?, ?, ?, ?, 'Normal');`,
          [a.PLOP, a.SUB, a.TAG, a.Nombre_cientifico_limpio, a.GENERO]
        );
      }
      console.log('¡Censo precargado exitosamente en SQLite local!');
    }

    return true;
  } catch (error) {
    console.error('Error inicializando SQLite:', error);
    return false;
  }
};

export const executeSql = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    if (!db) {
      return reject(new Error('Base de datos no inicializada'));
    }
    if (db.runAsync) {
      db.runAsync(sql, params)
        .then(res => resolve(res))
        .catch(err => reject(err));
    } else {
      db.transaction(tx => {
        tx.executeSql(
          sql,
          params,
          (_, result) => resolve(result),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    }
  });
};

export const querySql = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    if (!db) {
      return reject(new Error('Base de datos no inicializada'));
    }
    if (db.getAllAsync) {
      db.getAllAsync(sql, params)
        .then(rows => resolve(rows))
        .catch(err => reject(err));
    } else {
      db.transaction(tx => {
        tx.executeSql(
          sql,
          params,
          (_, { rows }) => resolve(rows._array || []),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    }
  });
};

export default {
  initDatabase,
  executeSql,
  querySql,
};
