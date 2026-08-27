// Multi-Model Ensemble Weather Engine (Tambopata Regional Quadrant)
// Coordenadas: -13.138° S, -69.618° W (Tambopata Research Center / Colpa Colorado)

const TAMBOPATA_LAT = -13.138;
const TAMBOPATA_LON = -69.618;

let cachedForecast = null;

export const getPronosticoRegional = async () => {
  try {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${TAMBOPATA_LAT}&longitude=${TAMBOPATA_LON}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max&hourly=temperature_2m,relativehumidity_2m,precipitation_probability,precipitation&timezone=America%2FLima&forecast_days=7`;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }

    const data = await response.json();
    
    // Procesar datos para la jornada de campo
    const hoy = {
      fecha: data.daily.time[0],
      tempMax: Math.round(data.daily.temperature_2m_max[0]),
      tempMin: Math.round(data.daily.temperature_2m_min[0]),
      probLluvia: data.daily.precipitation_probability_max[0] || 0,
      precipitacionMm: data.daily.precipitation_sum[0] || 0,
      humedadRelativa: Math.round(data.hourly.relativehumidity_2m[12] || 85),
    };

    const manana = {
      fecha: data.daily.time[1],
      tempMax: Math.round(data.daily.temperature_2m_max[1]),
      tempMin: Math.round(data.daily.temperature_2m_min[1]),
      probLluvia: data.daily.precipitation_probability_max[1] || 0,
      precipitacionMm: data.daily.precipitation_sum[1] || 0,
    };

    // Recomendación práctica de campo
    let recomendacion = "Jornada favorable para evaluar parcelas.";
    let ventanaOptima = "06:00 a 13:00";

    if (manana.probLluvia > 70 || manana.precipitacionMm > 15) {
      recomendacion = "⚠️ Alta probabilidad de aguacero tropical. Se recomienda salir a trocha temprano.";
      ventanaOptima = "05:30 a 10:30 am";
    } else if (manana.tempMax > 34) {
      recomendacion = "☀️ Día caluroso y despejado. Hidratación constante en trochas de Tierra Firme.";
      ventanaOptima = "06:00 a 11:30 am";
    }

    const resultado = {
      online: true,
      timestamp: Date.now(),
      cuadrante: "Reserva Nacional Tambopata (10x10 km)",
      hoy,
      manana,
      recomendacion,
      ventanaOptima,
      diasSemana: data.daily.time.map((t, idx) => ({
        fecha: t,
        max: Math.round(data.daily.temperature_2m_max[idx]),
        min: Math.round(data.daily.temperature_2m_min[idx]),
        prob: data.daily.precipitation_probability_max[idx] || 0,
        mm: data.daily.precipitation_sum[idx] || 0
      }))
    };

    cachedForecast = resultado;
    return resultado;
  } catch (error) {
    console.warn('Sin conexión a internet. Usando pronóstico en caché o valores climatológicos normales:', error);
    
    if (cachedForecast) {
      return { ...cachedForecast, online: false };
    }

    // Climatología promedio de Tambopata
    return {
      online: false,
      timestamp: Date.now(),
      cuadrante: "Reserva Nacional Tambopata (Climatología Histórica)",
      hoy: {
        fecha: new Date().toISOString().split('T')[0],
        tempMax: 31,
        tempMin: 22,
        probLluvia: 45,
        precipitacionMm: 8,
        humedadRelativa: 88,
      },
      manana: {
        fecha: new Date(Date.now() + 86400000).toISOString().split('T')[0],
        tempMax: 32,
        tempMin: 22,
        probLluvia: 50,
        precipitacionMm: 10,
      },
      recomendacion: "Modo Offline: Monitoreo con climatología estándar.",
      ventanaOptima: "06:00 a 12:00"
    };
  }
};
