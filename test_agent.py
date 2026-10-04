import json
import subprocess
import sys

def send_request(proc, method, params=None):
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method
    }
    if params is not None:
        req["params"] = params
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()
    response = proc.stdout.readline()
    print(f"Request: {method} -> Response: {response.strip()}")

def main():
    proc = subprocess.Popen(
        [".\\tinui.exe", "agent"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    send_request(proc, "build", {"entry": "valid.tin", "target": "dist"})
    
    proc.stdin.close()
    proc.wait()
    
    stderr = proc.stderr.read()
    if stderr:
        print(f"Stderr: {stderr}")

if __name__ == "__main__":
    main()
