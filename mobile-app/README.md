# 📱 The Macaw Society · App Móvil de Fenología Tambopata (React Native + Expo)

Aplicación móvil desarrollada para el registro fenológico en campo **100% Offline** en la **Reserva Nacional de Tambopata**, con catálogo precargado de **1,939 árboles individuales en 25 parcelas georreferenciadas**.

---

## 🦜 Características Principales

1. **🎬 Splash Screen Animado:**
   * Isotipo oficial de *The Macaw Society* y dos guacamayos animados volando hacia los laterales al iniciar.
2. **👤 Acceso sin Contraseñas:**
   * Selector rápido de perfil de evaluador (`👨‍🌾 Tío`, `👩‍🔬 Tesistas`, etc.).
3. **💾 100% Offline con SQLite:**
   * Toda la base de datos de 1,939 árboles (*Mauritia flexuosa*, *Socratea*, *Dipteryx*, *Bertholletia*, etc.) viaja dentro del celular. Funciona en modo avión en medio de la selva sin señal.
4. **🧭 Navegación Jerárquica de Trocha:**
   * Selección en 3 toques: **Hábitat** (Tierra Firme, Aguajal, Bajío, Sucesional) $\rightarrow$ **Parcela** (TF1..TF5, AG1..AG9, etc.) $\rightarrow$ **Subparcela** (1a, 1b..).
5. **📝 Planilla de Alto Contraste (Modo Fango/Lluvia):**
   * Botones táctiles grandes (0, 1, 2, 3, 4) para `Botón (B)`, `Flor (F)`, `Fruto Verde (FV)`, `Fruto Maduro (FM)` y `Diseminado (D)`.
   * Estado vital del árbol (`Normal`, `Desramado`, `Caído / Muerto`, `Nuevo`).
6. **📤 Exportador de Respaldo CSV Oficial:**
   * Genera el archivo con la nomenclatura reglamentaria:
     $$\mathbf{[HÁBITAT][PARCELA]\_[DDMMAA].csv}$$
   * **Ejemplo Bosque de Bajío Parcela FP1 el 28 de Dic:** `BBFP1_281226.csv`
   * **Ejemplo Bosque de Tierra Firme Parcela TF1 el 28 de Dic:** `BTFTF1_281226.csv`
   * Permite compartir inmediatamente por **WhatsApp**, **Bluetooth** o guardar en el teléfono.
7. **🌤️ Pronóstico Meteorológico Ensamble (10x10 km):**
   * Al detectar WiFi, consulta modelos ECMWF + GFS + FLDAS para las coordenadas de Tambopata (`-13.138, -69.618`), pronosticando lluvia (mm, %) y temperaturas para las caminatas de los 10 días de campaña.
8. **🔄 Sincronización Supabase:**
   * Subida de evaluaciones en lote hacia la nube con prevención de duplicados vía UUID.

---

## 🚀 Cómo Ejecutar la App en el Celular

### 1. Requisitos Previos
* Tener instalado [Node.js](https://nodejs.org/).
* Instalar la app gratuita **Expo Go** en tu celular Android (Google Play) o iPhone (App Store).

### 2. Iniciar el Servidor de Desarrollo
Abre una terminal en la carpeta `mobile-app` y ejecuta:

```bash
npm install
npx expo start
```

### 3. Abrir en el Celular
1. Escanea el código QR que aparece en la terminal con la cámara de tu iPhone o desde la app **Expo Go** en Android.
2. ¡Listo! La app cargará en tu teléfono y funcionará completamente sin conexión a internet.
