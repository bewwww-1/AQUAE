from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB_PATH = Path(__file__).with_name("database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE,
        description TEXT
    );
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        price REAL NOT NULL CHECK(price >= 0),
        stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
        description TEXT,
        FOREIGN KEY(category_id) REFERENCES categories(category_id)
    );
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        email TEXT UNIQUE,
        address TEXT
    );
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL DEFAULT 0 CHECK(total_amount >= 0),
        status TEXT NOT NULL DEFAULT 'Pending',
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    );
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        unit_price REAL NOT NULL CHECK(unit_price >= 0),
        subtotal REAL NOT NULL CHECK(subtotal >= 0),
        FOREIGN KEY(order_id) REFERENCES orders(order_id),
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    );
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        payment_date TEXT,
        amount REAL NOT NULL CHECK(amount >= 0),
        payment_method TEXT NOT NULL,
        payment_status TEXT NOT NULL DEFAULT 'Pending',
        FOREIGN KEY(order_id) REFERENCES orders(order_id)
    );
    """)
    conn.commit()
    seed_data(conn)
    conn.close()

def seed_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM categories")
    if cur.fetchone()[0] > 0:
        return

    categories = [
        ("Freshwater Fish", "ปลาน้ำจืดหลากหลายสายพันธุ์"),
        ("Aquatic Plants", "ไม้น้ำสำหรับตู้ปลา"),
        ("Aquarium Equipment", "อุปกรณ์และเครื่องกรอง"),
        ("Fish Food", "อาหารปลาและอาหารเสริม"),
        ("Decorations", "ของตกแต่งตู้ปลา"),
        ("Water Care", "ผลิตภัณฑ์ดูแลคุณภาพน้ำ"),
        ("Aquarium Tanks", "ตู้ปลาและชุดตู้"),
        ("Substrate", "วัสดุปูพื้นตู้ปลา"),
        ("Lighting", "ไฟสำหรับตู้ปลา"),
        ("Accessories", "อุปกรณ์เสริม")
    ]
    cur.executemany("INSERT INTO categories(category_name,description) VALUES (?,?)", categories)

    products = [
        (1,"Neon Tetra",35,80,"ปลาฝูงขนาดเล็ก สีสันสดใส"),
        (1,"Betta Halfmoon",180,25,"ปลากัดหางพระจันทร์"),
        (2,"Java Fern",95,40,"ไม้น้ำดูแลง่าย"),
        (2,"Anubias Nana",120,32,"อนูเบียสใบเล็ก"),
        (3,"Aqua Filter Pro",650,12,"เครื่องกรองน้ำสำหรับตู้กลาง"),
        (3,"Air Pump Mini",290,20,"ปั๊มลมขนาดเล็ก"),
        (4,"Tropical Fish Food",150,55,"อาหารปลาเขตร้อน"),
        (5,"Dragon Stone",220,30,"หินตกแต่งตู้ปลา"),
        (6,"Water Conditioner",190,45,"ปรับสภาพน้ำประปา"),
        (7,"Crystal Tank 24 inch",1850,8,"ตู้ปลากระจกใส 24 นิ้ว")
    ]
    cur.executemany("""INSERT INTO products(category_id,product_name,price,stock,description)
                       VALUES (?,?,?,?,?)""", products)

    customers = [
        ("Anan S.","0810000001","anan@example.com","Bangkok"),
        ("Benjamas K.","0810000002","benja@example.com","Nonthaburi"),
        ("Chaiwat P.","0810000003","chai@example.com","Pathum Thani"),
        ("Darika T.","0810000004","darika@example.com","Bangkok"),
        ("Ekachai M.","0810000005","ekachai@example.com","Samut Prakan"),
        ("Fah S.","0810000006","fah@example.com","Bangkok"),
        ("Gunn R.","0810000007","gunn@example.com","Ayutthaya"),
        ("Hana W.","0810000008","hana@example.com","Bangkok"),
        ("Ittipon L.","0810000009","itti@example.com","Chonburi"),
        ("Jirada N.","0810000010","jirada@example.com","Nakhon Pathom")
    ]
    cur.executemany("""INSERT INTO customers(customer_name,phone,email,address)
                       VALUES (?,?,?,?)""", customers)

    orders = [
        (1,"2026-11-01",250,"Paid"),(2,"2026-11-02",360,"Paid"),
        (3,"2026-11-03",650,"Pending"),(4,"2026-11-04",190,"Paid"),
        (5,"2026-11-05",440,"Paid"),(6,"2026-11-06",180,"Pending"),
        (7,"2026-11-07",290,"Paid"),(8,"2026-11-08",310,"Paid"),
        (9,"2026-11-09",1850,"Paid"),(10,"2026-11-10",335,"Pending")
    ]
    cur.executemany("""INSERT INTO orders(customer_id,order_date,total_amount,status)
                       VALUES (?,?,?,?)""", orders)

    items = [
        (1,1,2,35,70),(1,7,1,150,150),(1,9,1,30,30),
        (2,3,2,95,190),(2,4,1,120,120),(2,7,1,50,50),
        (3,5,1,650,650),(4,9,1,190,190),(5,8,2,220,440),
        (6,2,1,180,180),(7,6,1,290,290),(8,3,1,95,95),
        (8,4,1,120,120),(8,9,1,95,95),(9,10,1,1850,1850),
        (10,1,5,35,175),(10,7,1,160,160)
    ]
    cur.executemany("""INSERT INTO order_items(order_id,product_id,quantity,unit_price,subtotal)
                       VALUES (?,?,?,?,?)""", items)

    payments = [
        (1,"2026-11-01",250,"Transfer","Paid"),
        (2,"2026-11-02",360,"QR PromptPay","Paid"),
        (3,None,650,"Transfer","Pending"),
        (4,"2026-11-04",190,"Cash","Paid"),
        (5,"2026-11-05",440,"QR PromptPay","Paid"),
        (6,None,180,"Cash","Pending"),
        (7,"2026-11-07",290,"Transfer","Paid"),
        (8,"2026-11-08",310,"QR PromptPay","Paid"),
        (9,"2026-11-09",1850,"Transfer","Paid"),
        (10,None,335,"QR PromptPay","Pending")
    ]
    cur.executemany("""INSERT INTO payments(order_id,payment_date,amount,payment_method,payment_status)
                       VALUES (?,?,?,?,?)""", payments)
    conn.commit()

@app.route("/")
def dashboard():
    conn = get_db()
    stats = {
        "products": conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
        "customers": conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
        "orders": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "sales": conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE status='Paid'").fetchone()[0]
    }
    recent = conn.execute("""
        SELECT o.order_id, c.customer_name, o.order_date, o.total_amount, o.status
        FROM orders o JOIN customers c ON o.customer_id=c.customer_id
        ORDER BY o.order_id DESC LIMIT 6
    """).fetchall()
    conn.close()
    return render_template("index.html", stats=stats, recent=recent)

@app.route("/products")
def products():
    q = request.args.get("q", "").strip()
    conn = get_db()
    rows = conn.execute("""
        SELECT p.*, c.category_name
        FROM products p JOIN categories c ON p.category_id=c.category_id
        WHERE p.product_name LIKE ? ORDER BY p.product_id DESC
    """, (f"%{q}%",)).fetchall()
    conn.close()
    return render_template("products.html", products=rows, q=q)

@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories ORDER BY category_name").fetchall()
    if request.method == "POST":
        try:
            conn.execute("""INSERT INTO products(category_id,product_name,price,stock,description)
                            VALUES (?,?,?,?,?)""",
                         (request.form["category_id"], request.form["product_name"].strip(),
                          float(request.form["price"]), int(request.form["stock"]),
                          request.form.get("description", "").strip()))
            conn.commit()
            flash("เพิ่มสินค้าเรียบร้อยแล้ว", "success")
            conn.close()
            return redirect(url_for("products"))
        except (ValueError, sqlite3.IntegrityError) as exc:
            flash(f"ไม่สามารถบันทึกข้อมูลได้: {exc}", "error")
    conn.close()
    return render_template("product_form.html", categories=categories, product=None, page_title="Add Product")

@app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone()
    if product is None:
        conn.close()
        flash("ไม่พบสินค้าที่ต้องการ", "error")
        return redirect(url_for("products"))
    categories = conn.execute("SELECT * FROM categories ORDER BY category_name").fetchall()
    if request.method == "POST":
        try:
            conn.execute("""UPDATE products
                            SET category_id=?, product_name=?, price=?, stock=?, description=?
                            WHERE product_id=?""",
                         (request.form["category_id"], request.form["product_name"].strip(),
                          float(request.form["price"]), int(request.form["stock"]),
                          request.form.get("description", "").strip(), product_id))
            conn.commit()
            flash("แก้ไขสินค้าเรียบร้อยแล้ว", "success")
            conn.close()
            return redirect(url_for("products"))
        except (ValueError, sqlite3.IntegrityError) as exc:
            flash(f"ไม่สามารถแก้ไขข้อมูลได้: {exc}", "error")
    conn.close()
    return render_template("product_form.html", categories=categories, product=product, page_title="Edit Product")

@app.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM products WHERE product_id=?", (product_id,))
        conn.commit()
        flash("ลบสินค้าเรียบร้อยแล้ว", "success")
    except sqlite3.IntegrityError:
        flash("ไม่สามารถลบสินค้าได้ เนื่องจากมีสินค้าอยู่ในประวัติคำสั่งซื้อ", "error")
    conn.close()
    return redirect(url_for("products"))

@app.route("/orders")
def orders():
    conn = get_db()
    rows = conn.execute("""
        SELECT o.order_id, c.customer_name, o.order_date, o.total_amount, o.status,
               p.payment_method, p.payment_status
        FROM orders o JOIN customers c ON o.customer_id=c.customer_id
        LEFT JOIN payments p ON p.order_id=o.order_id
        ORDER BY o.order_id DESC
    """).fetchall()
    conn.close()
    return render_template("orders.html", orders=rows)

@app.route("/customers")
def customers():
    conn = get_db()
    rows = conn.execute("SELECT * FROM customers ORDER BY customer_id DESC").fetchall()
    conn.close()
    return render_template("customers.html", customers=rows)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
