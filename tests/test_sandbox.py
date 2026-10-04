import json
import subprocess
import sys
import threading
import time

def send_request(proc, method, params=None, msg_id=None):
    req = {
        "jsonrpc": "2.0",
        "method": method
    }
    if msg_id is not None:
        req["id"] = msg_id
    if params is not None:
        req["params"] = params
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()

def read_responses(proc, responses_dict, lock):
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        try:
            resp = json.loads(line)
            if "id" in resp:
                with lock:
                    responses_dict[resp["id"]] = resp
        except json.JSONDecodeError:
            pass

def main():
    print("Starting agent...")
    proc = subprocess.Popen(
        [".\\tinui.exe", "agent"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    responses = {}
    lock = threading.Lock()
    
    reader_thread = threading.Thread(target=read_responses, args=(proc, responses, lock))
    reader_thread.daemon = True
    reader_thread.start()

    # Query with traversal
    send_request(proc, "query", {
        "kind": "hover",
        "document": "../../../secret.txt",
        "position": {"line": 1, "character": 4}
    }, msg_id=1)
    
    # Query with Windows traversal
    send_request(proc, "query", {
        "kind": "hover",
        "document": "C:\\Windows\\System32\\cmd.exe",
        "position": {"line": 1, "character": 4}
    }, msg_id=2)
    
    time.sleep(1) # Wait for responses

    with lock:
        res_1 = responses.get(1, {})
        res_2 = responses.get(2, {})

    print("Result 1:", res_1)
    print("Result 2:", res_2)
    
    assert "error" in res_1 and "TIN-0004 Workspace Boundary Violation" in res_1["error"]["message"]
    assert "error" in res_2 and "TIN-0004 Workspace Boundary Violation" in res_2["error"]["message"]

    send_request(proc, "shutdown", msg_id=99)
    proc.wait()
    
    print("Sandbox tests passed successfully.")

if __name__ == "__main__":
    main()
