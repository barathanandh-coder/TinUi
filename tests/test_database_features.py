import unittest
import os
import tinpyui as tin

class TestDatabaseFeatures(unittest.TestCase):
    def setUp(self):
        self.db = tin.Database(":memory:")
        self.users = self.db.table("users")

    def tearDown(self):
        self.db.close()
        for f in ["test_export.json", "test_export.csv", "test_store.db"]:
            if os.path.exists(f):
                try: os.remove(f)
                except Exception: pass

    def test_table_crud(self):
        # 1. Insert & Auto Schema Generation
        u1_id = self.users.insert(name="Alice", role="Admin", age=30)
        u2_id = self.users.insert(name="Bob", role="Developer", age=25)
        u3_id = self.users.insert(name="Charlie", role="Developer", age=22)

        self.assertEqual(u1_id, 1)
        self.assertEqual(self.users.count(), 3)

        # 2. Get by ID / Filter
        alice = self.users.get(id=u1_id)
        self.assertIsNotNone(alice)
        self.assertEqual(alice["name"], "Alice")
        self.assertEqual(alice["role"], "Admin")

        # 3. Query Builder (where, order_by, limit)
        devs = self.users.where(role="Developer").order_by("age", desc=True).all()
        self.assertEqual(len(devs), 2)
        self.assertEqual(devs[0]["name"], "Bob")
        self.assertEqual(devs[1]["name"], "Charlie")

        # 4. Greater than filter
        older = self.users.where().gt("age", 23).all()
        self.assertEqual(len(older), 2)

        # 5. Update
        updated_count = self.users.update(where={"id": u2_id}, role="Lead Developer")
        self.assertEqual(updated_count, 1)
        bob = self.users.get(id=u2_id)
        self.assertEqual(bob["role"], "Lead Developer")

        # 6. Upsert
        self.users.upsert(where={"name": "Alice"}, role="SuperAdmin")
        alice_updated = self.users.get(name="Alice")
        self.assertEqual(alice_updated["role"], "SuperAdmin")

        # 7. Delete
        del_count = self.users.delete(name="Charlie")
        self.assertEqual(del_count, 1)
        self.assertEqual(self.users.count(), 2)

    def test_live_query_reactivity(self):
        live_users = self.users.live_query()
        initial_count = len(live_users.value)
        self.assertEqual(initial_count, 0)

        # Listen for reactive signal updates
        notification_events = []
        live_users.subscribe(lambda val: notification_events.append(len(val)))

        # Insert record -> live query should auto-update
        self.users.insert(name="Dave", role="Manager")
        self.assertEqual(len(live_users.value), 1)
        self.assertEqual(live_users.value[0]["name"], "Dave")
        self.assertEqual(len(notification_events), 1)

        # Update record -> live query auto-updates
        self.users.update(where={"name": "Dave"}, role="Director")
        self.assertEqual(live_users.value[0]["role"], "Director")
        self.assertEqual(len(notification_events), 2)

        # Delete record -> live query auto-updates
        self.users.delete(name="Dave")
        self.assertEqual(len(live_users.value), 0)
        self.assertEqual(len(notification_events), 3)

    def test_key_value_store(self):
        store = tin.KeyValueStore(":memory:")
        store.set("theme", "cyber-dark")
        store.set("font_size", 16)

        self.assertEqual(store.get("theme"), "cyber-dark")
        self.assertEqual(store.get("font_size"), 16)
        self.assertEqual(store.get("non_existent", default=42), 42)

        # Reactive Signal test
        theme_sig = store.signal("theme")
        self.assertEqual(theme_sig.value, "cyber-dark")

        # Updating signal updates store
        theme_sig.value = "light"
        self.assertEqual(store.get("theme"), "light")

    def test_declarative_model(self):
        @tin.model
        class Product:
            name: str
            price: float
            stock: int

        # Create
        p1 = Product.create(name="Cyber Deck", price=499.99, stock=10)
        self.assertEqual(p1["name"], "Cyber Deck")
        self.assertEqual(Product.count(), 1)

        # Query
        all_prods = Product.all()
        self.assertEqual(len(all_prods), 1)

        # Live query
        live_prods = Product.live_query()
        self.assertEqual(len(live_prods.value), 1)

    def test_json_and_csv_portability(self):
        self.users.insert(name="Test1", role="Role1")
        self.users.insert(name="Test2", role="Role2")

        # JSON Export & Import
        json_path = "test_export.json"
        self.db.export_json(json_path)
        self.assertTrue(os.path.exists(json_path))

        new_db = tin.Database(":memory:")
        new_db.import_json(json_path)
        self.assertEqual(new_db.table("users").count(), 2)
        new_db.close()

        # CSV Export & Import
        csv_path = "test_export.csv"
        self.db.export_csv("users", csv_path)
        self.assertTrue(os.path.exists(csv_path))

        csv_db = tin.Database(":memory:")
        csv_db.import_csv("users", csv_path)
        self.assertEqual(csv_db.table("users").count(), 2)
        csv_db.close()

    def test_low_code_components(self):
        table = self.db.table("tasks")
        table.insert(title="Implement Database", done=True)
        table.insert(title="Add Documentation", done=False)

        # LiveDataTable instantiation
        grid = tin.LiveDataTable(table)
        self.assertEqual(grid.tag, "DataTable")
        self.assertIn("columns", grid.props)
        self.assertIn("data", grid.props)

        # AutoCRUD instantiation
        crud = tin.AutoCRUD(table, title="Task Manager")
        self.assertEqual(crud.tag, "Card")
        self.assertEqual(len(crud.children), 3) # Heading, Spacer, LiveDataTable

if __name__ == "__main__":
    unittest.main()
