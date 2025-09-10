def generate_report(findings, output="report.txt"):
    """
    Genera un reporte básico con los hallazgos.
    """
    with open(output, "w") as f:
        f.write("SeedAudit Report\n")
        f.write("================\n\n")
        if not findings:
            f.write("✅ No se detectaron RNG inseguros.\n")
        else:
            f.write("⚠️ Hallazgos:\n")
            for fnd in findings:
                f.write(f"- {fnd['file']}:{fnd['line']} :: {fnd['match']}\n")
