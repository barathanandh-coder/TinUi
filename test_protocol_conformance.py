import json
import subprocess
import unittest
from jsonschema import validate

class TestProtocolConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("docs/architecture/machine_protocol_schema.json", "r") as f:
            cls.schema = json.load(f)
            
        cls.proc = subprocess.Popen(
            [".\\tinui.exe", "agent"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    @classmethod
    def tearDownClass(cls):
        cls.proc.stdin.close()
        cls.proc.wait()

    def send_request(self, method, params=None):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method
        }
        if params is not None:
            req["params"] = params
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        
        response_str = self.proc.stdout.readline().strip()
        response = json.loads(response_str)
        return response

    def test_initialize(self):
        res = self.send_request("initialize")
        validate(instance=res, schema=self.schema["definitions"]["ProtocolEnvelope"])
        validate(instance=res["result"], schema=self.schema["definitions"]["InitializeResponse"])

    def test_check_valid(self):
        with open("valid.tin", "w") as f:
            f.write("component Main():\n    Row():\n        Text(text=\"Hello\")")
        res = self.send_request("check", {"entry": "valid.tin"})
        validate(instance=res, schema=self.schema["definitions"]["ProtocolEnvelope"])

    def test_check_invalid(self):
        with open("invalid.tin", "w") as f:
            f.write("component Main():\n    Row(class: \"test\"):\n        Text(text=\"Hello\")")
        res = self.send_request("check", {"entry": "invalid.tin"})
        validate(instance=res, schema=self.schema["definitions"]["ProtocolEnvelope"])
        diagnostics = res["result"]["diagnostics"]
        self.assertTrue(len(diagnostics) > 0)
        for diag in diagnostics:
            validate(instance=diag, schema=self.schema["definitions"]["Diagnostic"])

    def test_build(self):
        res = self.send_request("build", {"entry": "valid.tin", "target": "dist"})
        validate(instance=res, schema=self.schema["definitions"]["ProtocolEnvelope"])

if __name__ == "__main__":
    unittest.main()
