import os
import ast

def scan_repo(path):
    """Escanea los archivos .py en un directorio buscando RNG inseguros."""
    findings = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=file_path)
                    except SyntaxError:
                        continue

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                            if hasattr(node.func.value, "id") and node.func.value.id == "random":
                                findings.append((file_path, node.lineno, "Uso de random encontrado"))
    return findings
