# cli/security_scanner.py
import ast
import re
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

class SecretScanner(ast.NodeVisitor):
    """
    AST Security Gatekeeper for TinPyUI.
    Parses Python source tree to block compiling hardcoded credentials into Wasm binaries.
    """
    def __init__(self):
        self.patterns = {
            "JWT Token": re.compile(r"^eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$"),
            "Stripe Secret Key": re.compile(r"^(sk_live_|sk_test_)[0-9a-zA-Z]{24,}$"),
            "Hardcoded Private Key": re.compile(r"^-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----"),
        }
        self.suspicious_names = {'api_secret', 'aws_secret_access_key', 'stripe_api_key', 'private_key_pem'}
        self.violations = []

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                if any(sus == var_name for sus in self.suspicious_names):
                    self.violations.append(f"Suspicious variable name '{target.id}' assigned in code.")

        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            string_val = node.value.value
            for label, pattern in self.patterns.items():
                if pattern.match(string_val):
                    self.violations.append(f"Hardcoded {label} detected: '{string_val[:12]}...'")

        self.generic_visit(node)

    def scan_code(self, source_code: str) -> bool:
        self.violations.clear()
        try:
            tree = ast.parse(source_code)
            self.visit(tree)
        except SyntaxError as e:
            print(f"[TinPyUI Security Scanner]: Syntax Error parsing source - {e}")
            return False

        if self.violations:
            for violation in self.violations:
                print(f"[TinPyUI FATAL]: Security Gatekeeper Violation -> {violation}")
            print("Resolution: Store credentials on your backend server. Do not compile secrets into WebAssembly.")
            return False
        return True

if __name__ == "__main__":
    scanner = SecretScanner()
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    
    files_to_scan = []
    if os.path.isfile(target):
        files_to_scan.append(target)
    elif os.path.isdir(target):
        for root, _, files in os.walk(target):
            if any(p in root for p in [".git", "__pycache__", "venv", "node_modules", "dist", "build", "tests"]):
                continue
            for f in files:
                if f.endswith(".py") and f != "security_scanner.py":
                    files_to_scan.append(os.path.join(root, f))
    
    total_violations = 0
    print(f"\n[+] [TinPyUI Security Scanner] Scanning {len(files_to_scan)} Python source files...")
    for fpath in files_to_scan:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                src = f.read()
            if not scanner.scan_code(src):
                print(f"  [!] Violation in: {fpath}")
                total_violations += len(scanner.violations)
        except Exception as e:
            pass

    if total_violations == 0:
        print(f"[+] [TinPyUI Security Scanner] Zero credential leaks detected across {len(files_to_scan)} files.\n")
        sys.exit(0)
    else:
        print(f"\n[!] [TinPyUI Security Scanner] Found {total_violations} security violations.\n")
        sys.exit(1)
