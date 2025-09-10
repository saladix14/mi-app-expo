// Ejemplo de generador inseguro (para pruebas con el harness)
function genMnemonic() {
  return Math.random().toString(36).slice(2);
}

console.log(genMnemonic());
