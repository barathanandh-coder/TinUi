# TinPyUI Universal Database, Real-Time Streams & System Connections Guide

> **Version:** TinPyUI v1.7.0  
> **Target Platforms:** Windows (Win32/DirectX), macOS (Cocoa/Metal), Linux (GTK/WebKit), Web (WASM/WebGPU), Mobile (iOS/Android).

---

## Table of Contents
1. [Architecture Overview & Connection Matrix](#1-architecture-overview--connection-matrix)
2. [Universal Database Engine (`tin.connect`)](#2-universal-database-engine-tinconnect)
   - [2.1 PostgreSQL Relational Integration](#21-postgresql-relational-integration)
   - [2.2 MongoDB Document Integration](#22-mongodb-document-integration)
   - [2.3 SQLite & In-Memory Storage](#23-sqlite--in-memory-storage)
   - [2.4 Redis Key-Value & Reactive Pub/Sub Engine](#24-redis-key-value--reactive-pubsub-engine)
   - [2.5 DuckDB & ClickHouse Vectorized Analytical Engines](#25-duckdb--clickhouse-vectorized-analytical-engines)
3. [Reactive Live Queries (`LiveQuery`)](#3-reactive-live-queries-livequery)
4. [Low-Code UI Components (`LiveDataTable`, `AutoCRUD` & `DataGrid`)](#4-low-code-ui-components-livedatatable--autocrud)
5. [Persistent Key-Value Store (`tin.use_store`)](#5-persistent-key-value-store-tinuse_store)
6. [Declarative Active Record Models (`@tin.model`)](#6-declarative-active-record-models-tinmodel)
7. [Real-Time Streams (`use_socket` & `use_sse`)](#7-real-time-streams-use_socket--use_sse)
8. [Native OS Platform Channels (`PlatformBridge`)](#8-native-os-platform-channels-platformbridge)
9. [Dynamic WebAssembly Compilation (`app.export_ir`)](#9-dynamic-webassembly-compilation-appexport_ir)
10. [End-to-End Production Code Recipe](#10-end-to-end-production-code-recipe)

---

## 1. Architecture Overview & Connection Matrix

TinPyUI decouples the UI layer from the data and platform layers. Any data source—relational table, document collection, Redis pub/sub channel, DuckDB analytical stream, WebSocket packet, or disk key-value cell—pipes into a reactive `Signal` or `LiveQuery` that updates the UI at 120 FPS without manual refresh loops.

```
+-----------------------------------------------------------------------------------------------+
|                               TINPYUI UNIVERSAL SYSTEM ARCHITECTURE                           |
+-----------------------------------------------------------------------------------------------+
|                                                                                               |
|  [ DATA & BACKEND LAYER ]             [ STATE LAYER (120 FPS) ]        [ PRESENTATION & OS ]  |
|  - PostgreSQL (Relational SQL)    -->   LiveQuery Signal         -->   LiveDataTable Grid     |
|  - MongoDB (Document NoSQL)       -->   O(1) Signal Cell Graph   -->   AutoCRUD Dashboard     |
|  - Redis (Pub/Sub & Caching)      -->   pubsub_signal() Stream   -->   DataGrid & AIChat      |
|  - DuckDB (Vectorized Analytics)  -->   Analytical Live Signal   -->   Interactive SVG Charts |
|  - SQLite (Embedded File & RAM)   -->   Reactive Key-Value Store -->   VirtualStack Window    |
|  - WebSockets & SSE Streams       -->   Platform Channels        -->   Win32 / macOS / WASM   |
|                                                                                               |
+-----------------------------------------------------------------------------------------------+
```

---

## 2. Universal Database Engine (`tin.connect`)

The `tin.connect()` factory automatically identifies the protocol scheme and instantiates the matching database engine. If external drivers (`psycopg2`, `pymongo`, `redis`, `duckdb`) are not installed on the target machine, the engine seamlessly falls back to a zero-crash, embedded in-memory dialect engine.

```python
import tinpyui as tin

# 1. PostgreSQL (Relational Engine)
pg_db = tin.connect("postgres://user:password@localhost:5432/my_database")

# 2. MongoDB (Document NoSQL Engine)
mongo_db = tin.connect("mongodb://localhost:27017/my_database")

# 3. Redis (Reactive Cache & Pub/Sub Signals)
redis_db = tin.connect("redis://localhost:6379/0")

# 4. DuckDB (Vectorized Analytical Engine)
duck_db = tin.connect("duckdb://analytics.db")

# 5. ClickHouse (High-Throughput Analytics)
ch_db = tin.connect("clickhouse://localhost:9000/default")

# 6. SQLite / Local Disk File
sqlite_db = tin.connect("sqlite:///app_data.db")

# 7. In-Memory Ephemeral Engine
ram_db = tin.connect(":memory:")
```

---

### 2.1 PostgreSQL Relational Integration

#### Detailed Syntax Reference:

```python
# Select or dynamically create table
events = pg_db.table("analytics_events")

# 1. Single Insert (Dynamically creates table & columns if missing)
row_id: int = events.insert(
    event="user_signup", 
    user_id="usr_90", 
    duration_ms=45.2, 
    is_active=True
)

# 2. Bulk Insert (ACID single-transaction batch)
batch_ids: list[int] = events.insert_many([
    {"event": "page_view", "user_id": "usr_91", "duration_ms": 12.0},
    {"event": "checkout",  "user_id": "usr_90", "duration_ms": 180.5}
])

# 3. Upsert (Update if matching record exists; otherwise insert)
events.upsert(
    where={"user_id": "usr_90", "event": "user_signup"}, 
    duration_ms=42.0
)

# 4. Fluent Query Builder
active_records = (events.where(user_id="usr_90")
                        .gt("duration_ms", 20.0)
                        .like("event", "user_%")
                        .order_by("duration_ms", desc=True)
                        .limit(5)
                        .offset(0)
                        .all())

# 5. Single Record Lookup
first_match = events.get(id=row_id)

# 6. Updates & Deletes
updated_count: int = events.update(where={"user_id": "usr_90"}, is_active=False)
deleted_count: int = events.delete(where={"is_active": False})

# 7. Raw Parameterized SQL
results = pg_db.query("SELECT * FROM analytics_events WHERE duration_ms > ?", [30.0])
affected = pg_db.execute("UPDATE analytics_events SET status = ? WHERE id = ?", ["archived", 1])
```

---

### 2.2 MongoDB Document Integration

`MongoCollection` natively supports unstructured JSON documents, nested dot-notation paths, and MongoDB filtering operators.

#### Detailed Syntax Reference:

```python
products = mongo_db.collection("products")

# 1. Single Document Insert
res = products.insert_one({
    "title": "Quantum GPU Server",
    "category": "Hardware",
    "price": 12000,
    "specs": {
        "cores": 128, 
        "ram": "512GB", 
        "storage": "8TB NVMe"
    }
})
doc_id: str = res["inserted_id"]

# 2. Bulk Document Insert
products.insert_many([
    {"title": "Cyber Keyboard", "category": "Peripherals", "price": 150},
    {"title": "Holographic Display", "category": "Hardware", "price": 3500}
])

# 3. Nested Dot-Notation & MongoDB Operator Queries
heavy_servers = products.find({
    "category": "Hardware",
    "price": {"$gte": 3000, "$lte": 15000},
    "specs.ram": "512GB" # Nested dot notation
})

# Supported operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin

# 4. Single Document Find
item = products.find_one({"title": "Quantum GPU Server"})

# 5. Document Updates
products.update_one({"title": "Cyber Keyboard"}, {"$set": {"price": 129}})
products.update_many({"category": "Hardware"}, {"$set": {"status": "in_stock"}})

# 6. Document Deletions
products.delete_one({"title": "Cyber Keyboard"})
products.delete_many({"category": "Obsolete"})

# 7. Document Count
total_hardware: int = products.count_documents({"category": "Hardware"})
```

---

### 2.3 SQLite & In-Memory Storage

For zero-configuration desktop applications or embedded device environments:

```python
# Persistent file on disk
db = tin.Database("app_database.db")

# In-memory RAM database
mem_db = tin.Database(":memory:")

# Automatic 1-line table creation
users = db.table("users")
users.insert(username="admin", email="admin@corp.internal")
```

---

### 2.4 Redis Key-Value & Reactive Pub/Sub Engine

Connect to any local or cloud Redis instance with `tin.connect("redis://...")`. If the `redis` library is not installed, TinPyUI automatically falls back to a thread-safe, high-speed in-memory simulation with zero crashes.

#### Features:
- **Reactive Key Signals**: `db.signal("key")` binds a reactive `Signal` that auto-updates whenever the Redis key changes.
- **Reactive Pub/Sub Signals**: `db.pubsub_signal("channel")` binds a reactive `Signal` to broadcast channel messages directly to UI elements.
- **Hash & List Operations**: Full support for `hset`, `hget`, `hgetall`, `incr`, and TTL expirations.

```python
import tinpyui as tin

redis = tin.connect("redis://localhost:6379/0")

# 1. Key-Value Operations with Optional Expiry (seconds)
redis.set("user:session", {"user_id": 42, "role": "admin"}, ex=3600)
session_data = redis.get("user:session")

# 2. Atomic Counters
visitor_count = redis.incr("site:visitors", 1)

# 3. Hash Maps
redis.hset("device:101", "firmware", "v2.1.0")
redis.hset("device:101", "status", "online")
device_info = redis.hgetall("device:101")

# 4. Reactive Key Signal (Two-way automatic sync with UI)
theme_signal = redis.signal("user:theme", default="cyberpunk")

# 5. Reactive Pub/Sub Signal (Instant stream to UI)
alert_signal = redis.pubsub_signal("server_alerts")

# Publishing from anywhere in the application:
redis.publish("server_alerts", {"level": "CRITICAL", "msg": "Node overload"})
```

---

### 2.5 DuckDB & ClickHouse Vectorized Analytical Engines

For financial analytics, IoT sensor logging, and large-scale data science applications, TinPyUI integrates DuckDB and ClickHouse via `tin.connect("duckdb://...")` and `tin.connect("clickhouse://...")`.

#### Features:
- **Sub-Millisecond Vectorized Relational Queries**: Process millions of rows in memory.
- **Automatic Schema Mapping**: SQL queries return native Python dictionary rows and lists.
- **Background Analytical Live Queries**: Re-executes queries on a configurable interval and updates attached charts and data grids.

```python
import tinpyui as tin

# Embedded in-memory or on-disk columnar database
analytics = tin.connect("duckdb://metrics.db")

# 1. Direct DDL & Vectorized Execution
analytics.execute("""
    CREATE TABLE IF NOT EXISTS server_metrics (
        timestamp TIMESTAMP,
        cpu_usage DOUBLE,
        mem_mb INTEGER,
        datacenter VARCHAR
    )
""")

# 2. High-Performance Table Inserts
metrics_tbl = analytics.table("server_metrics")
metrics_tbl.insert(cpu_usage=84.2, mem_mb=4096, datacenter="us-east")

# 3. Reactive Live Query (Auto-refreshes every 1.0 second)
live_stats = analytics.live_query(
    "SELECT datacenter, AVG(cpu_usage) as avg_cpu FROM server_metrics GROUP BY datacenter",
    interval=1.0
)

# 4. Bind directly to a reactive DataGrid or SVG Chart:
grid = tin.DataGrid(data=live_stats)
chart = tin.BarChart(data=live_stats)
```

---

## 3. Reactive Live Queries (`LiveQuery`)


A `LiveQuery` is a specialized subclass of `tin.Signal`. It binds directly to a database table or MongoDB collection and updates its `.value` whenever any `insert`, `update`, `delete`, or `upsert` takes place.

### How it works:
1. `LiveQuery` executes the initial query and stores results.
2. It registers a listener on the underlying `Table` or `MongoCollection`.
3. When any write occurs, the query re-evaluates and notifies all attached UI components at 120 FPS.

```python
import tinpyui as tin

db = tin.connect("postgres://admin:secret@localhost:5432/app_db")
tasks = db.table("tasks")

# 1. Create a reactive live query
active_tasks = tasks.live_query(status="pending")

# 2. Bind directly to UI elements (VirtualList, DataTable, etc.)
with tin.Window(title="Real-Time Task Feed"):
    with tin.Section():
        tin.Heading("Live Task Feed")
        
        # Automatically updates when new records are inserted
        tin.VirtualList(items=active_tasks, item_height=45.0)

        # Mutating the database automatically refreshes the VirtualList
        tin.Button(
            "Add Task", 
            on_click=lambda: tasks.insert(title="Emergency Maintenance", status="pending")
        )
```

---

## 4. Low-Code UI Components (`LiveDataTable` & `AutoCRUD`)

TinPyUI includes high-level low-code components to generate data grids and complete CRUD dashboards in a single line.

### 4.1 `tin.LiveDataTable`
Automatically inspects the table or collection schema, discovers columns, and binds to live query signals:

```python
# Binds to PostgreSQL Table
tin.LiveDataTable(pg_db.table("analytics_events"))

# Binds to MongoDB Collection with custom explicit column subset
tin.LiveDataTable(
    mongo_db.collection("products"), 
    columns=["title", "price", "category"]
)
```

### 4.2 `tin.AutoCRUD`
Generates a complete administrative dashboard including:
- Header title
- Interactive live data grid
- Automatic schema reflection

```python
# 1-Line Full CRUD Interface
tin.AutoCRUD(db.table("inventory"), title="Warehouse Inventory")
tin.AutoCRUD(mongo_db.collection("customers"), title="Customer Directory")
```

---

## 5. Persistent Key-Value Store (`tin.use_store`)

A disk-persisted, thread-safe storage engine for user preferences, authentication tokens, and window geometry.

```python
# Initialize persistent store
store = tin.use_store("app_settings.db", table="preferences")

# Direct Get & Set
store.set("theme", "cyber-dark")
store.set("volume", 90)
current_theme = store.get("theme", default="cyber-dark")

# Disk-backed Reactive Signal
# Mutating the signal automatically writes to disk!
theme_sig = store.signal("theme", default="cyber-dark")
theme_sig.value = "neon-matrix"  # Instantly persisted to database
```

---

## 6. Declarative Active Record Models (`@tin.model`)

Define structured Active Record data models with Python class syntax:

```python
@tin.model
class Product:
    name: str
    price: float
    stock: int = 0
    category: str = "General"

# Create record
item = Product.create(name="Cyber Deck", price=499.0, stock=25, category="Hardware")

# Find & Query
all_items = Product.all()
hardware = Product.where(category="Hardware").order_by("price", desc=True).all()
first_match = Product.get(id=1)

# Reactive Live Query
live_stock = Product.live_query(category="Hardware")

# Delete
Product.delete(where={"stock": 0})
```

---

## 7. Real-Time Streams (`use_socket` & `use_sse`)

Connect to remote live servers, WebSockets, and Server-Sent Event (SSE) streams reactively.

### 7.1 WebSocket Connection (`tin.use_socket`)

```python
socket = tin.use_socket("wss://api.marketdata.com/v1/stream")

# socket.status  -> Signal ("connecting", "open", "closed", "error")
# socket.message -> Signal (contains last received payload)

with tin.Window(title="Live Market Feed"):
    with tin.Column(padding=20, gap=10):
        # Dynamic connection badge
        tin.Text(
            text=lambda: f"Status: {socket.status.value.upper()}",
            color=lambda: "#00f2fe" if socket.status.value == "open" else "#ff3b30"
        )
        
        # Live incoming message box
        tin.Text(text=lambda: f"Latest Payload: {socket.message.value}")
        
        # Send message
        tin.Button("Send Heartbeat", on_click=lambda: socket.send("PING"))
```

### 7.2 Server-Sent Events (`tin.use_sse`)

```python
live_feed = tin.use_sse("https://stream.wikimedia.org/v2/stream/recentchange")

# Element re-renders on every incoming event tick
tin.Text(text=live_feed, color="neon-cyan")
```

---

## 8. Native OS Platform Channels (`PlatformBridge`)

Interface directly with native desktop operating system dialogs and hardware features:

```python
# 1. Native Open File Dialog (Returns absolute path or None)
selected_file: Optional[str] = tin.PlatformBridge.open_file_dialog()

# 2. Native Save File Dialog (Returns selected save path or None)
save_destination: Optional[str] = tin.PlatformBridge.save_file_dialog()

# 3. Native Desktop Toast / Notification
tin.PlatformBridge.show_notification(
    title="Build Completed", 
    message="Native executable successfully compiled!"
)

# 4. Device Haptic Vibration Pulse
tin.PlatformBridge.vibrate(pattern_ms=50)

# 5. OS Clipboard Synchronization
tin.PlatformBridge.copy_clipboard("Copied from TinPyUI")
```

---

## 9. Dynamic WebAssembly Compilation (`app.export_ir`)

Compile declarative Python layout structures directly into dynamic Intermediate Representation JSON (`app.ir.json`) to serve in Go WebAssembly / WebGPU engines without running Python on the client.

```python
import tinpyui as tin

app = tin.Window(title="Dynamic Edge Blueprint", width=1280, height=800)
with app:
    with tin.Section():
        tin.Heading(text="Hardware Accelerated Edge", size="hero")
        tin.GradientText("Native WebAssembly Vector UI", gradient=["#00f2fe", "#9b51e0"])
        tin.Button(text="Launch Pipeline", variant="neon-cyan")

# Export to public/ for WebAssembly runtime consumption
app.export_ir("public/app.ir.json")
```

---

## 10. End-to-End Production Code Recipe

A complete production application combining **PostgreSQL / MongoDB connection**, **Real-Time WebSockets**, **LiveQuery data binding**, **Native OS File Dialogs**, and **1-Line AutoCRUD**:

```python
import tinpyui as tin

# 1. Initialize Database (PostgreSQL with embedded fallback)
db = tin.connect("postgres://admin:secret@localhost:5432/production_app")
orders = db.table("orders")

# 2. Real-Time WebSocket stream
stream = tin.use_socket("wss://api.marketstream.internal/v1/feed")

# 3. Persistent User Settings
settings = tin.use_store("app_settings.db")
theme = settings.signal("theme", default="cyber-dark")

# 4. Reactive Live Query
active_orders = orders.live_query(status="processing")

# 5. Declarative Multi-Panel Layout
app = tin.Window(title="TinPyUI Enterprise Command Console", width=1400, height=900)
with app:
    with tin.Row(padding=24, gap=24):
        # Left Panel: Controls & Telemetry
        with tin.Column(width=420, gap=16):
            tin.Heading("SYSTEM TELEMETRY", size="md", color="#00f2fe")
            
            tin.Card(padding=16):
                tin.Text(text=lambda: f"Stream Status: {stream.status.value.upper()}")
                tin.Text(text=lambda: f"Latest Telemetry: {stream.message.value}")
            
            tin.Button(
                "Create New Order",
                on_click=lambda: orders.insert(
                    customer="Global Logistics", 
                    amount=8450.0, 
                    status="processing"
                )
            )
            
            tin.Button(
                "Export Orders to CSV",
                on_click=lambda: orders.export_csv(
                    "orders", 
                    tin.PlatformBridge.save_file_dialog() or "orders_backup.csv"
                )
            )

        # Right Panel: 1-Line Live CRUD Grid
        with tin.Column(width="flex", gap=16):
            tin.AutoCRUD(orders, title="Active Orders Pipeline")

if __name__ == "__main__":
    tin.run(app)
```
