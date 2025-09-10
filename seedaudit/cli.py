import click
from seedaudit.scanner import scan_repo

@click.group()
def cli():
    """SeedAudit - Auditoría de RNG y generación de mnemonics"""
    pass

@cli.command()
@click.argument("path", type=click.Path(exists=True))
def scan(path):
    """Escanea el repositorio en PATH para encontrar RNG inseguros."""
    findings = scan_repo(path)
    if findings:
        click.echo("⚠️ Posibles RNG inseguros encontrados:")
        for file, lineno, msg in findings:
            click.echo(f"{file}:{lineno} -> {msg}")
    else:
        click.echo("✅ No se encontraron RNG inseguros.")
