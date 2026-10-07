import sqlite3

class ConexionBD:
    def __init__(self, db_name="restaurante.db"):
        self.db_name = db_name
        self.inicializar_base_datos()

    def conectar(self):
        return sqlite3.connect(self.db_name)

    def inicializar_base_datos(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        # Tabla de Mesas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mesas (
                numero INTEGER PRIMARY KEY,
                estado TEXT NOT NULL,
                tiene_pedido_abierto INTEGER NOT NULL
            )
        """)
        
        # Tabla de Pedidos (Transacción principal)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_mesa INTEGER,
                estado TEXT,
                FOREIGN KEY (numero_mesa) REFERENCES mesas(numero)
            )
        """)
        
        # Tabla de Detalles del Pedido (Líneas de detalle)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_pedidos (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER,
                nombre_item TEXT,
                cantidad INTEGER,
                subtotal INTEGER,
                FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
            )
        """)
        
        conexion.commit()
        conexion.close()

    def guardar_pedido_con_detalles(self, numero_mesa: int, items: list):
        conexion = self.conectar()
        cursor = conexion.cursor()
        try:
            # Consulta parametrizada (seguridad contra Inyección SQL)
            cursor.execute(
                "INSERT INTO pedidos (numero_mesa, estado) VALUES (?, ?)", 
                (numero_mesa, "Abierto")
            )
            id_pedido = cursor.lastrowid
            
            for item in items:
                cursor.execute(
                    "INSERT INTO detalle_pedidos (id_pedido, nombre_item, cantidad, subtotal) VALUES (?, ?, ?, ?)",
                    (id_pedido, item['nombre'], item['cantidad'], item['subtotal'])
                )
            conexion.commit()
            print("[Éxito] Transacción y líneas de detalle guardadas correctamente en la BD.")
        except Exception as e:
            conexion.rollback()
            print(f"[Error en BD] No se pudo guardar la transacción: {e}")
        finally:
            conexion.close()
