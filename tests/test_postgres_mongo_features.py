import unittest
import tinpyui as tin

class TestPostgresMongoFeatures(unittest.TestCase):
    def test_postgres_engine(self):
        pg_db = tin.connect("postgres://postgres:password@localhost:5432/test_db")
        self.assertIsInstance(pg_db, tin.PostgresDatabase)

        table = pg_db.table("analytics_events")
        # Insert
        e1_id = table.insert(event="user_login", user_id="usr_101", duration_ms=45.5)
        e2_id = table.insert(event="page_view", user_id="usr_102", duration_ms=12.0)
        e3_id = table.insert(event="checkout", user_id="usr_101", duration_ms=180.2)

        self.assertEqual(table.count(), 3)

        # Query
        user_101_events = table.where(user_id="usr_101").order_by("duration_ms", desc=True).all()
        self.assertEqual(len(user_101_events), 2)
        self.assertEqual(user_101_events[0]["event"], "checkout")

        # LiveQuery Reactivity on PostgresTable
        live_events = table.live_query(user_id="usr_101")
        self.assertEqual(len(live_events.value), 2)

        # Insert new matching event -> live query auto-updates
        table.insert(event="click_button", user_id="usr_101", duration_ms=5.0)
        self.assertEqual(len(live_events.value), 3)

        # UI Binding
        grid = tin.LiveDataTable(table)
        self.assertEqual(grid.tag, "DataTable")

        crud = tin.AutoCRUD(table, title="PostgreSQL Analytics")
        self.assertEqual(crud.tag, "Card")
        pg_db.close()

    def test_mongodb_engine(self):
        mongo_db = tin.connect("mongodb://localhost:27017/shop_db")
        self.assertIsInstance(mongo_db, tin.MongoDatabase)

        collection = mongo_db.collection("products")
        
        # 1. Native MongoDB insert_one & insert_many
        res1 = collection.insert_one({
            "title": "Quantum GPU Server",
            "category": "Hardware",
            "price": 12000,
            "specs": {"cores": 128, "ram": "512GB"}
        })
        self.assertIn("inserted_id", res1)

        collection.insert_many([
            {"title": "Cyber Keyboard", "category": "Peripherals", "price": 150, "specs": {"switch": "Mechanical"}},
            {"title": "Holographic Display", "category": "Hardware", "price": 3500, "specs": {"res": "8K", "ram": "64GB"}},
            {"title": "Neural Headset", "category": "Hardware", "price": 4999, "specs": {"latency": "1ms"}}
        ])

        self.assertEqual(collection.count_documents(), 4)

        # 2. Dot-Notation queries & MongoDB operators ($gt, $in)
        hw_items = collection.find({"category": "Hardware", "price": {"$gt": 3000}})
        self.assertEqual(len(hw_items), 3)

        # Nested dot-notation
        ram_items = collection.find({"specs.ram": "512GB"})
        self.assertEqual(len(ram_items), 1)
        self.assertEqual(ram_items[0]["title"], "Quantum GPU Server")

        # 3. Fluent where chaining
        cheap_items = collection.where(category="Hardware").lt("price", 5000).all()
        self.assertEqual(len(cheap_items), 2)

        # 4. Updates & Deletes
        collection.update_one({"title": "Cyber Keyboard"}, {"price": 129})
        updated_kb = collection.find_one({"title": "Cyber Keyboard"})
        self.assertEqual(updated_kb["price"], 129)

        collection.delete_one({"title": "Cyber Keyboard"})
        self.assertEqual(collection.count_documents(), 3)

        # 5. LiveQuery Reactivity on MongoDB Collections
        live_hw = collection.live_query(category="Hardware")
        self.assertEqual(len(live_hw.value), 3)

        collection.insert_one({"title": "Optic Router", "category": "Hardware", "price": 899})
        self.assertEqual(len(live_hw.value), 4)

        # 6. UI Binding
        grid = tin.LiveDataTable(collection)
        self.assertEqual(grid.tag, "DataTable")
        self.assertIn("title", grid.props.get("columns", []))

        crud = tin.AutoCRUD(collection, title="MongoDB Product Catalog")
        self.assertEqual(crud.tag, "Card")
        mongo_db.close()

    def test_connect_factory_dispatch(self):
        pg = tin.connect("postgres://u:p@localhost/db")
        self.assertIsInstance(pg, tin.PostgresDatabase)

        pg_alt = tin.connect("postgresql://u:p@localhost/db")
        self.assertIsInstance(pg_alt, tin.PostgresDatabase)

        mg = tin.connect("mongodb://localhost:27017/db")
        self.assertIsInstance(mg, tin.MongoDatabase)

        mg_srv = tin.connect("mongodb+srv://user:pass@cluster0.mongodb.net/db")
        self.assertIsInstance(mg_srv, tin.MongoDatabase)

        sq = tin.connect("sqlite:///:memory:")
        self.assertIsInstance(sq, tin.Database)

        mem = tin.connect(":memory:")
        self.assertIsInstance(mem, tin.Database)

        pg.close()
        pg_alt.close()
        mg.close()
        mg_srv.close()
        sq.close()
        mem.close()

if __name__ == "__main__":
    unittest.main()
