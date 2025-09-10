from seedaudit.scanner import scan_repo
import tempfile
import os

def test_detect_math_random():
    code = "let x = Math.random();"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as tmp:
        tmp.write(code.encode("utf-8"))
        tmp_path = tmp.name
    
    findings = scan_repo(os.path.dirname(tmp_path))
    assert any("Math.random" in f["match"] for f in findings)

    os.remove(tmp_path)
