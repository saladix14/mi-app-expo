#!/bin/bash
# Ejecuta el harness con el generador JS de ejemplo
seedaudit harness --cmd "node examples/js_generator_example.js" --runs 50 --out results.json
