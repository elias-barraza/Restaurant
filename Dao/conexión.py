import sqlite3
from datetime import datetime
from Models.excepciones import MesaOcupadaException, ReglaNegocioException

class ConexionBD:
    def __init__(self, db_name="restaurante.db"):
        self.db_name = db_name
        self.inicializar_base_datos()

    def conectar(self):
        conexion = sqlite3.connect(self.db_name)
        conexion.row_factory = sqlite3.Row
        return conexion

    def inicializar_base_datos(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        # 1. Tabla de Mesas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mesas (
                numero INTEGER PRIMARY KEY,
                estado TEXT NOT NULL,
                tiene_pedido_abierto INTEGER NOT NULL
            )
        """)
        
        # Insertar mesas iniciales (1 al 10) si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM mesas")
        if cursor.fetchone()[0] == 0:
            for num in range(1, 11):
                cursor.execute(
                    "INSERT INTO mesas (numero, estado, tiene_pedido_abierto) VALUES (?, ?, ?)",
                    (num, "Disponible", 0)
                )

        # 2. Tabla de Ítems del Menú (CRUD - P02, P03, P04, P05, P06, P09, P10, P11)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items_menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                precio INTEGER NOT NULL,
                tiempo_preparacion INTEGER NOT NULL,
                estacion_cocina TEXT NOT NULL,
                precio_usd REAL DEFAULT 0,
                con_alcohol INTEGER DEFAULT 0
            )
        """)

        # 3. Tabla de Pedidos (P12, P13, P14)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_mesa INTEGER,
                estado TEXT,
                total INTEGER DEFAULT 0,
                fecha_hora TEXT,
                FOREIGN KEY (numero_mesa) REFERENCES mesas(numero)
            )
        """)
        
        # 4. Tabla de Detalles del Pedido con Observación (P12, P13)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_pedidos (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER,
                nombre_item TEXT,
                tipo TEXT,
                cantidad INTEGER,
                observacion TEXT DEFAULT '',
                subtotal INTEGER,
                FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
            )
        """)
        
        # Migración: asegurar que la columna 'observacion' y 'tipo' existan si la tabla ya había sido creada
        cursor.execute("PRAGMA table_info(detalle_pedidos)")
        columnas_detalles = [col["name"] for col in cursor.fetchall()]
        if "observacion" not in columnas_detalles:
            cursor.execute("ALTER TABLE detalle_pedidos ADD COLUMN observacion TEXT DEFAULT ''")
        if "tipo" not in columnas_detalles:
            cursor.execute("ALTER TABLE detalle_pedidos ADD COLUMN tipo TEXT DEFAULT ''")

        cursor.execute("PRAGMA table_info(pedidos)")
        columnas_pedidos = [col["name"] for col in cursor.fetchall()]
        if "total" not in columnas_pedidos:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN total INTEGER DEFAULT 0")
        if "fecha_hora" not in columnas_pedidos:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN fecha_hora TEXT DEFAULT ''")

        # 5. Insertar ítems del menú iniciales si está vacío para facilitar pruebas
        cursor.execute("SELECT COUNT(*) FROM items_menu")
        if cursor.fetchone()[0] == 0:
            items_iniciales = [
                ("Lomo a lo Pobre", "Plato caliente", 8500, 25, "Cocina Caliente", 0, 0),
                ("Pastel de Choclo", "Plato caliente", 7500, 25, "Cocina Caliente", 0, 0),
                ("Bebida Cola", "Bebida", 2000, 5, "Bar", 0, 0),
                ("Vino Reserva", "Bebida", 0, 5, "Bar", 20.0, 1),
                ("Tiramisú", "Postre", 4000, 10, "Pastelería", 0, 0)
            ]
            cursor.executemany("""
                INSERT INTO items_menu (nombre, tipo, precio, tiempo_preparacion, estacion_cocina, precio_usd, con_alcohol)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, items_iniciales)

        conexion.commit()
        conexion.close()

    # =========================================================================
    # CRUD ÍTEMS DEL MENÚ (P02, P03, P04, P05, P06, P09, P10, P11)
    # =========================================================================
    def crear_item(self, nombre: str, tipo: str, precio: int, tiempo_preparacion: int = None, 
                   estacion_cocina: str = None, precio_usd: float = 0, con_alcohol: bool = False) -> int:
        """
        Crea un nuevo ítem del menú asociando automáticamente el tiempo de preparación
        y la estación de cocina correspondiente a su tipo si no se especifican.
        """
        tipo_normalizado = tipo.strip().capitalize()
        if "caliente" in tipo.lower() or "plato" in tipo.lower():
            tipo_final = "Plato caliente"
            tiempo_def = 25
            estacion_def = "Cocina Caliente"
        elif "bebida" in tipo.lower():
            tipo_final = "Bebida"
            tiempo_def = 5
            estacion_def = "Bar"
        elif "postre" in tipo.lower():
            tipo_final = "Postre"
            tiempo_def = 10
            estacion_def = "Pastelería"
        else:
            tipo_final = tipo_normalizado
            tiempo_def = 15
            estacion_def = "Cocina General"

        tiempo_final = tiempo_preparacion if tiempo_preparacion is not None else tiempo_def
        estacion_final = estacion_cocina if estacion_cocina is not None else estacion_def

        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO items_menu (nombre, tipo, precio, tiempo_preparacion, estacion_cocina, precio_usd, con_alcohol)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre.strip(), tipo_final, int(precio), tiempo_final, estacion_final, float(precio_usd), 1 if con_alcohol else 0))
        nuevo_id = cursor.lastrowid
        conexion.commit()
        conexion.close()
        return nuevo_id

    def listar_items(self) -> list:
        """Retorna todos los ítems del menú registrados en la base de datos."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, tipo, precio, tiempo_preparacion, estacion_cocina, precio_usd, con_alcohol FROM items_menu ORDER BY id ASC")
        filas = cursor.fetchall()
        items = [dict(fila) for fila in filas]
        conexion.close()
        return items

    def obtener_item_por_id(self, id_item: int):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM items_menu WHERE id = ?", (id_item,))
        fila = cursor.fetchone()
        conexion.close()
        return dict(fila) if fila else None

    def obtener_item_por_nombre(self, nombre: str):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM items_menu WHERE LOWER(nombre) = LOWER(?)", (nombre.strip(),))
        fila = cursor.fetchone()
        conexion.close()
        return dict(fila) if fila else None

    def modificar_precio_item(self, id_item: int, nuevo_precio: int) -> bool:
        """Modifica el precio de un ítem existente en la base de datos (P04)."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE items_menu SET precio = ? WHERE id = ?", (int(nuevo_precio), id_item))
        afectados = cursor.rowcount
        conexion.commit()
        conexion.close()
        return afectados > 0

    def eliminar_item(self, id_item: int) -> bool:
        """Elimina un ítem del menú de la base de datos (P06)."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM items_menu WHERE id = ?", (id_item,))
        afectados = cursor.rowcount
        conexion.commit()
        conexion.close()
        return afectados > 0

    # =========================================================================
    # GESTIÓN DE MESAS Y PEDIDOS (P12, P13, P14)
    # =========================================================================
    def mesa_tiene_pedido_abierto(self, numero_mesa: int) -> bool:
        """Verifica si la mesa indicada ya cuenta con un pedido abierto (P14)."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM pedidos 
            WHERE numero_mesa = ? AND estado = 'Abierto'
        """, (numero_mesa,))
        cuenta = cursor.fetchone()[0]
        conexion.close()
        return cuenta > 0

    def abrir_pedido_mesa(self, numero_mesa: int, items: list) -> int:
        """
        Abre un pedido para la mesa especificada y registra todas sus líneas de detalle.
        Si la mesa ya tiene un pedido abierto, arroja MesaOcupadaException (P14).
        """
        # Regla de negocio P14: Impedir segundo pedido en mesa abierta
        if self.mesa_tiene_pedido_abierto(numero_mesa):
            raise MesaOcupadaException(f"Error: La mesa {numero_mesa} ya tiene un pedido abierto y no se puede abrir otro.")

        conexion = self.conectar()
        cursor = conexion.cursor()
        try:
            total_pedido = sum(it.get("subtotal", 0) for it in items)
            fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                "INSERT INTO pedidos (numero_mesa, estado, total, fecha_hora) VALUES (?, ?, ?, ?)",
                (numero_mesa, "Abierto", total_pedido, fecha_str)
            )
            id_pedido = cursor.lastrowid

            # Actualizar estado de la mesa a Ocupada
            cursor.execute(
                "UPDATE mesas SET estado = 'Ocupada', tiene_pedido_abierto = 1 WHERE numero = ?",
                (numero_mesa,)
            )

            # Insertar líneas de detalle con su observación (P12, P13)
            for item in items:
                cursor.execute("""
                    INSERT INTO detalle_pedidos (id_pedido, nombre_item, tipo, cantidad, observacion, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    id_pedido,
                    item.get("nombre", "Item"),
                    item.get("tipo", ""),
                    item.get("cantidad", 1),
                    item.get("observacion", ""),
                    item.get("subtotal", 0)
                ))

            conexion.commit()
            return id_pedido
        except Exception as e:
            conexion.rollback()
            raise e
        finally:
            conexion.close()

    def guardar_pedido_con_detalles(self, numero_mesa: int, items: list) -> int:
        """Método de compatibilidad con versiones previas."""
        return self.abrir_pedido_mesa(numero_mesa, items)

    def listar_pedidos(self) -> list:
        """Lista todos los pedidos registrados."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_pedido, numero_mesa, estado, total, fecha_hora FROM pedidos ORDER BY id_pedido DESC")
        filas = cursor.fetchall()
        pedidos = [dict(fila) for fila in filas]
        conexion.close()
        return pedidos

    def obtener_pedido_con_detalles(self, id_pedido: int) -> dict:
        """Obtiene la cabecera y todas las líneas de detalle de un pedido (P13)."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT id_pedido, numero_mesa, estado, total, fecha_hora FROM pedidos WHERE id_pedido = ?", (id_pedido,))
        pedido_fila = cursor.fetchone()
        if not pedido_fila:
            conexion.close()
            return None

        pedido_dict = dict(pedido_fila)
        
        cursor.execute("""
            SELECT id_detalle, nombre_item, tipo, cantidad, observacion, subtotal 
            FROM detalle_pedidos 
            WHERE id_pedido = ? 
            ORDER BY id_detalle ASC
        """, (id_pedido,))
        detalles_filas = cursor.fetchall()
        pedido_dict["detalles"] = [dict(det) for det in detalles_filas]

        conexion.close()
        return pedido_dict

    def cerrar_pedido_mesa(self, id_pedido: int) -> bool:
        """Cierra el pedido y libera la mesa."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT numero_mesa FROM pedidos WHERE id_pedido = ?", (id_pedido,))
        fila = cursor.fetchone()
        if not fila:
            conexion.close()
            return False
        
        numero_mesa = fila["numero_mesa"]
        cursor.execute("UPDATE pedidos SET estado = 'Cerrado' WHERE id_pedido = ?", (id_pedido,))
        
        # Verificar si quedan otros pedidos abiertos para esta mesa
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE numero_mesa = ? AND estado = 'Abierto'", (numero_mesa,))
        abiertos = cursor.fetchone()[0]
        if abiertos == 0:
            cursor.execute("UPDATE mesas SET estado = 'Disponible', tiene_pedido_abierto = 0 WHERE numero = ?", (numero_mesa,))

        conexion.commit()
        conexion.close()
        return True
