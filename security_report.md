---
name: "Security report (Responsible Disclosure)"
about: "Reporte de seguridad — por favor no incluir exploits ni semillas en texto claro."
title: "Security report: [breve descripción]"
labels: ["security", "triage"]
assignees: []
---

**Resumen corto**
- Tipo: (RNG debil / Entropía baja / Uso de PRNG no criptográfico / Exposición de seeds en logs / Otro)
- Componentes afectados: (ruta/repositorio/archivo)
- Severidad sugerida: (Alta / Media / Baja)

**Descripción detallada**
Describe de forma concisa el problema observado (qué y dónde). Evitá instrucciones de explotación y no incluyas mnemonics en texto plano.

**Archivos / Líneas evidentes**
- `path/to/file.js:123` — breve snippet (máx. 6 líneas) que muestre el patrón inseguro, p. ej. `Math.random()`.

**Pruebas y evidencia (no PII, no seeds en claro)**
- Resultado del análisis: e.g. "El scanner detectó `Math.random` en X archivos. El harness estadístico (local) recolectó N muestras: tasa de duplicados = Y%, entropía empírica total ≈ Z bits."
- Adjuntar `results.json` generado por seedaudit (contiene métricas y hashes SHA256 de muestras; NO incluye seeds en claro por defecto).
- Si necesitás incluir semillas para reproducir (solo con autorización), especificá que se enviarán cifradas y solicitar permiso.

**Impacto**
- Explicá el impacto potencial si el código vulnerable se usa para generar seeds/privkeys: pérdida de fondos, compromisos de cuentas, etc.

**Recomendaciones (soluciones sugeridas)**
- Reemplazar `Math.random()` / `random.*` por CSPRNG:
  - Browser: `crypto.getRandomValues()`
  - Node.js: `crypto.randomBytes()`
  - Python: `secrets.token_bytes()` o `os.urandom()`
  - React Native: `react-native-securerandom` / `react-native-get-random-values`
- Agregar tests automáticos y bloqueo en CI que detecten PRNG inseguros en paths críticos.
- Realizar harness estadístico con seedaudit en build local y comparar métricas.
- Añadir passphrase BIP39 (opcional) y uso de hardware keystores para claves críticas.

**Timeline propuesto**
- Notificación inicial: hoy
- Parche preliminar: 24–72 horas (si severidad alta)
- Reporte final: 7 días hábiles (ajustable)

**Contacto del auditor**
- Nombre:
- Email:
- (Opcional) PGP key / método seguro para intercambio de secretos:

**Consentimiento / next steps**
- ¿Deseas que enviemos el `results.json` con métricas? (Sí / No)
- ¿Solicitan que enviemos seeds cifradas para reproducir? (Sí / No — si Sí, requerimos autorización por escrito y passphrase)
