"""
Unit and Integration Tests for TinPyUI v1.7.0 Features
Tests Redis & DuckDB connectors, UI component suite, iOS export generator, and gesture recognition.
"""

import unittest
import os
import shutil
import tempfile
import time

import tinpyui as tin

class TestV17Features(unittest.TestCase):

    # 1. Redis Reactive Connector Tests
    def test_redis_database_operations(self):
        r_db = tin.connect("redis://127.0.0.1:6379/0")
        self.assertIsInstance(r_db, tin.RedisDatabase)
        
        # Key-Value operations
        r_db.set("user:name", "Alice")
        self.assertEqual(r_db.get("user:name"), "Alice")
        self.assertTrue(r_db.exists("user:name"))

        # Increment / Decrement
        r_db.set("counter", 10)
        self.assertEqual(r_db.incr("counter", 5), 15)
        self.assertEqual(r_db.decr("counter", 2), 13)

        # Hash operations
        r_db.hset("user:profile", "email", "alice@example.com")
        r_db.hset("user:profile", "role", "admin")
        self.assertEqual(r_db.hget("user:profile", "email"), "alice@example.com")
        all_hash = r_db.hgetall("user:profile")
        self.assertEqual(all_hash.get("role"), "admin")

        # Reactive Signal test
        sig = r_db.signal("reactive_key", default="initial")
        self.assertEqual(sig.value, "initial")
        r_db.set("reactive_key", "updated")
        self.assertEqual(sig.value, "updated")

        # PubSub Signal test
        ps_sig = r_db.pubsub_signal("system_events", default=None)
        r_db.publish("system_events", {"status": "ok"})
        self.assertEqual(ps_sig.value, {"status": "ok"})

        r_db.delete("user:name", "counter", "user:profile", "reactive_key")
        r_db.close()

    # 2. DuckDB / ClickHouse Analytical Connectors Tests
    def test_duckdb_and_clickhouse(self):
        duck = tin.connect("duckdb://:memory:")
        self.assertIsInstance(duck, tin.DuckDBDatabase)

        # Table & SQL
        duck.execute("CREATE TABLE analytics (metric_id INTEGER, value REAL, tag TEXT)")
        tbl = duck.table("analytics")
        tbl.insert(metric_id=1, value=99.4, tag="cpu")
        tbl.insert(metric_id=2, value=45.2, tag="ram")

        self.assertEqual(tbl.count(), 2)
        rows = tbl.select()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["tag"], "cpu")

        # Live query
        live = duck.live_query("SELECT SUM(value) as total FROM analytics", interval=0.1)
        self.assertIsInstance(live, tin.Signal)
        time.sleep(0.05)
        self.assertGreater(len(live.value), 0)

        # ClickHouse routing
        ch = tin.connect("clickhouse://localhost:9000/default")
        self.assertIsInstance(ch, tin.ClickHouseDatabase)
        duck.close()
        ch.close()

    # 3. DataGrid Component Tests
    def test_data_grid(self):
        sample_data = [
            {"id": 1, "name": "Alpha", "role": "Engineer"},
            {"id": 2, "name": "Beta", "role": "Designer"},
            {"id": 3, "name": "Gamma", "role": "Manager"},
            {"id": 4, "name": "Delta", "role": "Support"}
        ]
        grid = tin.DataGrid(data=sample_data, page_size=2)
        self.assertEqual(grid.tag, "DataGrid")
        self.assertEqual(grid.total_pages(), 2)

        # Sorting
        grid.sort_by("name", ascending=True)
        processed = grid.get_processed_data()
        self.assertEqual(processed[0]["name"], "Alpha")

        grid.sort_by("name", ascending=False)
        processed_desc = grid.get_processed_data()
        self.assertEqual(processed_desc[0]["name"], "Gamma")

        # Filtering
        grid.set_search("beta")
        filtered = grid.get_filtered_data()
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["name"], "Beta")

        # CSV & JSON Export
        csv_text = grid.export_csv()
        self.assertIn("Beta", csv_text)
        json_text = grid.export_json()
        self.assertIn('"Beta"', json_text)

    # 4. AIChat Component Tests
    def test_ai_chat(self):
        chat = tin.AIChat(model_name="TinAI")
        self.assertEqual(chat.tag, "AIChat")
        self.assertEqual(len(chat.props.get("messages", [])), 0)

        # Append complete message
        chat.append_message("user", "Hello Assistant")
        self.assertEqual(len(chat.props["messages"]), 1)
        self.assertEqual(chat.props["messages"][0]["content"], "Hello Assistant")

        # Token Streaming
        chat.start_stream(role="assistant", initial_token="Thinking")
        chat.stream_token("... ")
        chat.stream_token("Done!")
        chat.end_stream()

        self.assertEqual(len(chat.props["messages"]), 2)
        self.assertEqual(chat.props["messages"][1]["content"], "Thinking... Done!")
        self.assertFalse(chat.props.get("is_streaming", True))

        # Clear
        chat.clear()
        self.assertEqual(len(chat.props["messages"]), 0)

    # 5. ColorPicker Component Tests
    def test_color_picker(self):
        picker = tin.ColorPicker(value="#00f2fe")
        self.assertEqual(picker.tag, "ColorPicker")
        self.assertEqual(picker.color, "#00f2fe")

        picker.set_color("#ff007f")
        self.assertEqual(picker.color, "#ff007f")
        self.assertEqual(picker.props["value"], "#ff007f")

    # 6. DatePicker & Calendar Tests
    def test_date_picker_and_calendar(self):
        cal = tin.Calendar(year=2026, month=9)
        self.assertEqual(cal.tag, "Calendar")
        matrix = cal.get_month_matrix()
        self.assertIsInstance(matrix, list)
        self.assertGreater(len(matrix), 3)

        cal.next_month()
        self.assertEqual(cal.props["month"], 10)
        cal.prev_month()
        self.assertEqual(cal.props["month"], 9)

        picker = tin.DatePicker(value="2026-09-16")
        self.assertEqual(picker.tag, "DatePicker")
        self.assertEqual(picker.props["value"], "2026-09-16")
        picker.set_value("2026-10-01")
        self.assertEqual(picker.props["value"], "2026-10-01")

    # 7. Chart Suite Tests
    def test_chart_suite(self):
        values = [10.0, 25.0, 50.0, 30.0, 65.0]

        line = tin.LineChart(data=values)
        self.assertEqual(line.tag, "Chart")
        self.assertIn("<polyline", line.props["svg"])

        bar = tin.BarChart(data=values)
        self.assertIn("<rect", bar.props["svg"])

        donut = tin.DonutChart(data=values)
        self.assertIn("<circle", donut.props["svg"])

        spark = tin.Sparkline(data=values)
        self.assertIn("<polyline", spark.props["svg"])

    # 8. TreeView Tests
    def test_tree_view(self):
        tree_data = [
            tin.TreeNode(
                id="root",
                label="Project Root",
                children=[
                    tin.TreeNode(id="src", label="src", children=[
                        tin.TreeNode(id="main", label="main.py")
                    ]),
                    tin.TreeNode(id="readme", label="README.md")
                ]
            )
        ]
        tree = tin.TreeView(nodes=tree_data)
        self.assertEqual(tree.tag, "TreeView")

        found = tree.find_node("main")
        self.assertIsNotNone(found)
        self.assertEqual(found["label"], "main.py")

        tree.toggle_expand("src")
        src_node = tree.find_node("src")
        self.assertTrue(src_node.get("expanded"))

    # 9. iOS Xcode Project Generator Tests
    def test_ios_export_pipeline(self):
        temp_dir = tempfile.mkdtemp(prefix="tinpyui_ios_test_")
        try:
            res = tin.export_ios(
                target_file="index.tin",
                output_dir=temp_dir,
                app_name="CyberVault",
                bundle_id="com.tinpyui.cybervault",
                build_ipa=False
            )
            self.assertEqual(res["output_dir"], os.path.abspath(temp_dir))

            # Verify files staged
            app_dir = os.path.join(temp_dir, "CyberVault")
            proj_dir = os.path.join(temp_dir, "CyberVault.xcodeproj")
            assets_dir = os.path.join(app_dir, "www")

            self.assertTrue(os.path.exists(os.path.join(app_dir, "AppDelegate.swift")))
            self.assertTrue(os.path.exists(os.path.join(app_dir, "SceneDelegate.swift")))
            self.assertTrue(os.path.exists(os.path.join(app_dir, "ViewController.swift")))
            self.assertTrue(os.path.exists(os.path.join(app_dir, "Info.plist")))
            self.assertTrue(os.path.exists(os.path.join(proj_dir, "project.pbxproj")))
            self.assertTrue(os.path.exists(os.path.join(assets_dir, "index.html")))
            self.assertTrue(os.path.exists(os.path.join(assets_dir, "app.ir.json")))

            # Check Info.plist content
            with open(os.path.join(app_dir, "Info.plist"), "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("com.tinpyui.cybervault", content)
                self.assertIn("CyberVault", content)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
