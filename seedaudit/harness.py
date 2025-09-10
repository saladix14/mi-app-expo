#!/usr/bin/env python3
"""
seedaudit.harness

Modo laboratorio para ejecutar repetidamente un generador de mnemonics (comando local),
recolectar muestras y calcular métricas estadísticas (colisiones, entropía por posición,
chi² aproximado, top-words).

USO EJEMPLO:
  python -m seedaudit.harness --cmd "node scripts/gen_mnemonic.js" --runs 2000 --out /tmp/results.json

IMPORTANTE (SEGURIDAD):
- Por defecto NO se almacenan mnemonics en texto claro: se guarda sólo sha256(mnemonic).
- Si necesitás guardar mnemonics, usá --save-seeds --encrypt; se solicitará passphrase.
- Ejecutar únicamente en builds locales o entornos autorizados.
"""
from __future__ import annotations
import argparse
import subprocess
import json
import sys
import math
from collections import Counter, defaultdict
from hashlib import sha256
from getpass import getpass
from pathlib import Path
from typing import List, Dict, Any

# Optional: encryption support
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import constant_time
    import os
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

WORDLIST_SIZE = 2048
IDEAL_BITS_PER_WORD = math.log2(WORDLIST_SIZE)  # ~11

def run_command_once(cmd: str, timeout: int = 30) -> str:
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    out = p.stdout.strip()
    if not out:
        out = p.stderr.strip()
    return out

def shannon_entropy(counter: Counter, total: int) -> float:
    ent = 0.0
    for _, c in counter.items():
        p = c / total
        if p > 0:
            ent -= p * math.log2(p)
    return ent

def chi2_approx(counter: Counter, total: int, vocab_size: int = WORDLIST_SIZE) -> float:
    expected = total / vocab_size
    chi2 = 0.0
    observed_words = set(counter.keys())
    for w in observed_words:
        o = counter[w]
        chi2 += (o - expected) ** 2 / expected
    missing = vocab_size - len(observed_words)
    if missing > 0:
        chi2 += missing * expected  # (0 - expected)^2 / expected = expected
    return chi2

def derive_key_from_passphrase(passphrase: str, salt: bytes = None) -> (bytes, bytes):
    if salt is None:
        salt = b"seedaudit-salt-2025"  # could be randomized per-file; deterministic default ok for simple use
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000)
    key = kdf.derive(passphrase.encode("utf-8"))
    return key, salt

def encrypt_bytes(data: bytes, passphrase: str) -> Dict[str, str]:
    salt = os.urandom(16)
    key, _ = derive_key_from_passphrase(passphrase, salt=salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data, None)
    return {
        "salt_hex": salt.hex(),
        "nonce_hex": nonce.hex(),
        "cipher_hex": ct.hex()
    }

def analyze_mnemonics(mnemonics: List[str]) -> Dict[str, Any]:
    total = len(mnemonics)
    uniq = len(set(mnemonics))
    duplicates = total - uniq

    per_position = defaultdict(Counter)
    global_counter = Counter()

    for m in mnemonics:
        words = m.split()
        for i, w in enumerate(words):
            per_position[i][w] += 1
            global_counter[w] += 1

    pos_stats = {}
    total_entropy_est = 0.0
    for pos, counter in per_position.items():
        pos_total = sum(counter.values())
        ent = shannon_entropy(counter, pos_total)
        chi2 = chi2_approx(counter, pos_total)
        pos_stats[pos] = {
            "entropy_bits": ent,
            "ideal_bits": IDEAL_BITS_PER_WORD,
            "chi2_approx": chi2,
            "distinct_words": len(counter),
            "total_samples": pos_total
        }
        total_entropy_est += ent

    top_global = global_counter.most_common(30)
    return {
        "total_samples": total,
        "unique_mnemonics": uniq,
        "duplicates": duplicates,
        "duplicate_rate": duplicates / total if total else 0.0,
        "per_position": {k: v for k, v in pos_stats.items()},
        "top_global": top_global,
        "estimated_total_entropy_bits": total_entropy_est,
        "ideal_total_entropy_bits": IDEAL_BITS_PER_WORD * 12
    }

def main():
    ap = argparse.ArgumentParser(description="SeedAudit harness: collect mnemonics and analyze RNG quality.")
    ap.add_argument("--cmd", required=True, help="Comando que genera UNA mnemonic y la imprime por stdout.")
    ap.add_argument("--runs", type=int, default=1000, help="Número de ejecuciones a recolectar.")
    ap.add_argument("--out", help="Archivo JSON de salida con métricas (no contiene mnemonics en texto por defecto).")
    ap.add_argument("--save-seeds", action="store_true", help="Guardar mnemonics en el archivo de salida (REQUIERE --encrypt).")
    ap.add_argument("--encrypt", action="store_true", help="Cifrar las semillas antes de guardarlas (si --save-seeds).")
    ap.add_argument("--wordlist-size", type=int, default=WORDLIST_SIZE)
    args = ap.parse_args()

    if args.save_seeds and args.encrypt and not CRYPTO_AVAILABLE:
        print("[ERROR] La librería cryptography no está disponible. Instalarla para usar --encrypt.")
        sys.exit(1)

    collected = []
    hashes = []
    print("ATENCIÓN: Ejecutar solo en entornos autorizados. Recolectando muestras...")
    for i in range(args.runs):
        try:
            out = run_command_once(args.cmd)
        except Exception as e:
            print(f"[ERROR] Ejecutando comando: {e}")
            break
        if not out:
            print(f"[WARN] ejecución {i+1} produjo salida vacía. Ignorando.")
            continue
        line = out.splitlines()[0].strip()
        words = line.split()
        # filtramos a mnemonics de 12 palabras explícitamente
        if len(words) != 12:
            print(f"[WARN] ejecución {i+1} resultó en {len(words)} palabras. (Se esperaba 12). Ignorando.")
            continue
        collected.append(line)
        h = sha256(line.encode("utf-8")).hexdigest()
        hashes.append(h)
        if (i + 1) % max(1, args.runs // 10) == 0:
            print(f"  -> {i+1}/{args.runs} muestras recolectadas")

    if not collected:
        print("[RESULT] No se recolectaron mnemonics válidas.")
        sys.exit(0)

    metrics = analyze_mnemonics(collected)

    out_payload: Dict[str, Any] = {
        "metadata": {
            "cmd": args.cmd,
            "runs_requested": args.runs,
            "runs_collected": len(collected)
        },
        "metrics": metrics,
        # by default do not include clear mnemonic values
        "samples_hashes_sha256": hashes
    }

    if args.save_seeds:
        if not args.encrypt:
            print("[ERROR] --save-seeds requiere --encrypt para almacenar semillas completas de forma segura.")
            sys.exit(1)
        passphrase = getpass("Passphrase para cifrar las semillas (no se mostrará): ")
        # join mnemonics to single bytes blob and encrypt
        blob = ("\n".join(collected)).encode("utf-8")
        enc = encrypt_bytes(blob, passphrase)
        out_payload["encrypted_seeds"] = enc
        print("[INFO] Semillas cifradas y añadidas al payload.")

    if args.out:
        outpath = Path(args.out)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(out_payload, f, indent=2)
        print(f"[OK] Resultado guardado en {outpath}")

    # Resumen legible
    print("\n=== RESUMEN ===")
    print(f"Muestras recolectadas: {metrics['total_samples']}")
    print(f"Unicas: {metrics['unique_mnemonics']}  | Duplicadas: {metrics['duplicates']}  | Tasa duplicados: {metrics['duplicate_rate']:.6%}")
    print(f"Entropía empírica total aproximada: {metrics['estimated_total_entropy_bits']:.2f} bits (ideal ≈ {metrics['ideal_total_entropy_bits']:.2f} bits)")
    print("Top palabras globales (posible sesgo):")
    for w, c in metrics["top_global"][:20]:
        pct = c / (metrics["total_samples"] * 12)
        print(f"  {w:12s} -> {c:6d} ({pct:.6%} del total de palabras)")

if __name__ == "__main__":
    main()
