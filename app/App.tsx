import React, { useState } from 'react';
import { SafeAreaView, View, Text, TouchableOpacity, TextInput, ScrollView, StyleSheet, ActivityIndicator } from 'react-native';

/**
 * SeedAudit Expo — Comic Dark MVP
 * - Botón Escanear que llama a POST /api/scan (backend)
 * - Muestra listado de findings (mock/real)
 * - Modal consentimiento simplificado (inline here)
 *
 * Nota: este código es intentionally minimal para que funcione en Expo.
 */

export default function App() {
  const [view, setView] = useState<'home'|'scan'|'report'|'billing'>('home');
  const [loading, setLoading] = useState(false);
  const [findings, setFindings] = useState<any[]>([]);
  const [reportMeta, setReportMeta] = useState<any | null>(null);
  const [repoPath, setRepoPath] = useState<string>('');
  const [consentGiven, setConsentGiven] = useState(false);

  async function runScan() {
    if (!consentGiven) {
      alert('Debés aceptar el consentimiento antes de ejecutar el scan.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('http://10.0.2.2:8000/api/scan', { // emulador Android: 10.0.2.2
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: repoPath || 'repo-local', anonymize: true })
      });
      const json = await res.json();
      setFindings(json.findings || []);
      setReportMeta({ id: json.report_id, created: json.created });
      setView('report');
    } catch (e) {
      console.warn(e);
      alert('Error contactando backend. Revisá consola.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.root}>
      <View style={styles.header}>
        <View style={styles.logo}><Text style={styles.logoText}>S</Text></View>
        <View>
          <Text style={styles.title}>SeedAudit</Text>
          <Text style={styles.subtitle}>Auditoría de RNG · Comic Dark</Text>
        </View>
      </View>

      <ScrollView style={styles.main}>
        {view === 'home' && (
          <View style={styles.card}>
            <Text style={styles.h1}>Protegé tus seeds</Text>
            <Text style={styles.p}>Detectamos RNG inseguros y generamos reportes anonimizados por defecto.</Text>
            <TouchableOpacity style={styles.primaryBtn} onPress={() => setView('scan')}>
              <Text style={styles.primaryBtnText}>Escanear</Text>
            </TouchableOpacity>
          </View>
        )}

        {view === 'scan' && (
          <View style={styles.card}>
            <Text style={styles.h2}>Escaneo</Text>
            <TextInput
              placeholder="Repositorio (path o URL)"
              placeholderTextColor="#999"
              onChangeText={setRepoPath}
              style={styles.input}
              value={repoPath}
            />
            <View style={{ flexDirection: 'row', gap: 12 }}>
              <TouchableOpacity style={styles.primaryBtn} onPress={runScan}>
                {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.primaryBtnText}>Iniciar Escaneo</Text>}
              </TouchableOpacity>
              <TouchableOpacity style={styles.secondaryBtn} onPress={() => { setConsentGiven(!consentGiven) }}>
                <Text style={styles.secondaryBtnText}>{consentGiven ? 'Consentimiento OK' : 'Aceptar consentimiento'}</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.note}>Modo safe: semillas reales no se envían sin consentimiento explícito.</Text>
          </View>
        )}

        {view === 'report' && (
          <View style={styles.card}>
            <Text style={styles.h2}>Reporte</Text>
            {!reportMeta && <Text style={styles.p}>No hay reportes todavía.</Text>}
            {reportMeta && (
              <>
                <Text style={styles.small}>ID: {reportMeta.id ?? 'local'}</Text>
                <Text style={styles.small}>Fecha: {reportMeta.created ?? new Date().toISOString()}</Text>
                <View style={{ marginTop: 12 }}>
                  {findings.length === 0 && <Text style={styles.p}>Sin hallazgos.</Text>}
                  {findings.map((f, i) => (
                    <View key={i} style={styles.finding}>
                      <Text style={styles.findingFile}>{f.file}:{f.line}</Text>
                      <Text style={styles.findingSnippet}>{f.snippet}</Text>
                      <Text style={styles.findingSeverity}>{(f.severity||'low').toUpperCase()}</Text>
                    </View>
                  ))}
                </View>
              </>
            )}
          </View>
        )}

        {view === 'billing' && (
          <View style={styles.card}>
            <Text style={styles.h2}>Cuenta</Text>
            <Text style={styles.p}>Planes mock: Free / Pro. Para producción integrar Stripe server-side.</Text>
          </View>
        )}

      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity onPress={()=>setView('home')}><Text style={styles.footerLink}>Inicio</Text></TouchableOpacity>
        <TouchableOpacity onPress={()=>setView('scan')}><Text style={styles.footerLink}>Escanear</Text></TouchableOpacity>
        <TouchableOpacity onPress={()=>setView('report')}><Text style={styles.footerLink}>Reportes</Text></TouchableOpacity>
        <TouchableOpacity onPress={()=>setView('billing')}><Text style={styles.footerLink}>Cuenta</Text></TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0b0b0f', color: '#fff' },
  header: { flexDirection: 'row', gap: 12, padding: 16, alignItems: 'center' },
  logo: { width: 56, height: 56, borderRadius: 10, backgroundColor: '#7b61ff', alignItems: 'center', justifyContent: 'center', transform: [{ rotate: '-8deg' }] },
  logoText: { color: '#fff', fontSize: 22, fontWeight: '900' },
  title: { color: '#fff', fontSize: 20, fontWeight: '900' },
  subtitle: { color: '#bdbdbd', fontSize: 12 },
  main: { padding: 16 },
  card: { backgroundColor: '#0f0f13', padding: 16, borderRadius: 12, marginBottom: 12, borderWidth: 1, borderColor: '#222' },
  h1: { color: '#fff', fontSize: 22, fontWeight: '900', marginBottom: 8 },
  h2: { color: '#fff', fontSize: 18, fontWeight: '800', marginBottom: 8 },
  p: { color: '#cfcfcf', marginBottom: 12 },
  input: { backgroundColor: '#0b0b0d', color: '#fff', padding: 12, borderRadius: 8, borderWidth: 1, borderColor: '#222', marginBottom: 12 },
  primaryBtn: { backgroundColor: '#ff7ab6', padding: 12, borderRadius: 8, minWidth: 140, alignItems: 'center' },
  primaryBtnText: { color: '#fff', fontWeight: '800' },
  secondaryBtn: { borderWidth: 1, borderColor: '#333', padding: 12, borderRadius: 8, minWidth: 140, alignItems: 'center'},
  secondaryBtnText: { color: '#fff' },
  note: { color: '#9a9a9a', marginTop: 8, fontSize: 12 },
  footer: { padding: 12, flexDirection: 'row', justifyContent: 'space-around', borderTopWidth: 1, borderTopColor: '#111' },
  footerLink: { color: '#bdbdbd' },
  small: { color: '#9a9a9a', fontSize: 12 },
  finding: { backgroundColor: '#080808', padding: 8, marginBottom: 8, borderRadius: 8 },
  findingFile: { color: '#fff', fontWeight: '700' },
  findingSnippet: { color: '#cfcfcf', fontFamily: 'monospace' },
  findingSeverity: { color: '#ffa' }
});
