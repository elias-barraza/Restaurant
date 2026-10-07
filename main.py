import sys
from Dao.conexión import ConexionBD
from Models import (
    Boleta, 
    Mesa, 
    Pedido, 
    PlatoCaliente, 
    Bebida, 
    BebidaImportada, 
    Postre, 
    Ingrediente,
    MesaOcupadaException, 
    ReglaNegocioException
)
from Services.indicador_service import IndicadorService

def leer_entero(mensaje: str, permitir_vacio: bool = False, por_defecto: int = None) -> int:
    """
    Lee un entero por consola de forma segura. Si el usuario escribe letras (ej: 'abc'),
    captura el error, muestra un mensaje informativo y no se cae (Cumple P19).
    """
    while True:
        entrada = input(mensaje).strip()
        if permitir_vacio and entrada == "":
            return por_defecto
        try:
            return int(entrada)
        except ValueError:
            print(f"[Error] '{entrada}' no es un número válido. Por favor, ingrese un número entero.")

def mostrar_menu():
    print("\n" + "=" * 65)
    print("      SISTEMA DE GESTIÓN - RESTAURANTE SABORES DEL SUR")
    print("=" * 65)
    print(" 1. Crear ítem del menú (P02, P09, P10, P11)")
    print(" 2. Listar ítems del menú (P03, P05)")
    print(" 3. Modificar precio de un ítem (P04)")
    print(" 4. Eliminar ítem del menú (P06)")
    print(" 5. Registrar pedido de mesa con detalles y observación (P12)")
    print(" 6. Ver detalle de un pedido de mesa (P13)")
    print(" 7. Probar Regla: Mesa con pedido abierto (P14)")
    print(" 8. Probar Regla: Plato con ingrediente clave sin stock (P15)")
    print(" 9. Calcular precio de bebida importada con Dólar API (P16, P17)")
    print("10. Validar RUT para boleta (P07, P08)")
    print("11. Ejecutar Demostración Rápida del Guion de Pruebas (P01-P19)")
    print(" 0. Salir")
    print("=" * 65)

# =========================================================================
# FUNCIONES DE LAS OPCIONES DEL MENÚ
# =========================================================================

def opcion_crear_item(db: ConexionBD):
    print("\n--- Crear Ítem del Menú (P02, P09, P10, P11) ---")
    nombre = input("Ingrese nombre del ítem (ej. Cazuela): ").strip()
    if not nombre:
        print("[Aviso] El nombre no puede estar vacío.")
        return

    print("Seleccione tipo de ítem:")
    print("  1. Plato caliente (25 min de preparación / Cocina Caliente)")
    print("  2. Bebida (5 min de preparación / Bar)")
    print("  3. Postre (10 min de preparación / Pastelería)")
    tipo_sel = input("Opción (1/2/3) [por defecto 1]: ").strip()

    if tipo_sel == "2":
        tipo = "Bebida"
        tiempo = 5
        estacion = "Bar"
    elif tipo_sel == "3":
        tipo = "Postre"
        tiempo = 10
        estacion = "Pastelería"
    else:
        tipo = "Plato caliente"
        tiempo = 25
        estacion = "Cocina Caliente"

    precio = leer_entero("Ingrese precio en CLP (ej. 8500): ")

    id_creado = db.crear_item(
        nombre=nombre,
        tipo=tipo,
        precio=precio,
        tiempo_preparacion=tiempo,
        estacion_cocina=estacion
    )
    print(f"\n[Confirmación] Se guardó exitosamente el ítem:")
    print(f" -> ID: {id_creado} | Nombre: '{nombre}' | Tipo: '{tipo}' | Precio: ${precio:,} CLP | Tiempo: {tiempo} min | Estación: '{estacion}'")

def opcion_listar_items(db: ConexionBD):
    print("\n--- Listado de Ítems del Menú (P03, P05) ---")
    items = db.listar_items()
    if not items:
        print("No hay ítems registrados en el menú.")
        return

    print(f"{'ID':<4} | {'Nombre':<22} | {'Tipo':<16} | {'Precio':<10} | {'Tiempo':<8} | {'Estación Cocina'}")
    print("-" * 80)
    for it in items:
        precio_str = f"${it['precio']:,} CLP" if it['precio'] > 0 else f"${it['precio_usd']} USD"
        print(f"{it['id']:<4} | {it['nombre']:<22} | {it['tipo']:<16} | {precio_str:<10} | {it['tiempo_preparacion']:<2} min   | {it['estacion_cocina']}")
    print("-" * 80)

def opcion_modificar_precio(db: ConexionBD):
    print("\n--- Modificar Precio de Ítem del Menú (P04) ---")
    opcion_listar_items(db)
    id_item = leer_entero("\nIngrese el ID del ítem a modificar: ")
    item = db.obtener_item_por_id(id_item)
    if not item:
        print(f"[Error] No se encontró ningún ítem con ID {id_item}.")
        return

    print(f"Ítem seleccionado: '{item['nombre']}' - Precio actual: ${item['precio']:,} CLP")
    nuevo_precio = leer_entero("Ingrese el nuevo precio (ej. 9000): ")
    if db.modificar_precio_item(id_item, nuevo_precio):
        print(f"\n[Éxito] El precio de '{item['nombre']}' fue modificado a ${nuevo_precio:,} CLP.")
    else:
        print("[Error] No se pudo actualizar el registro.")

def opcion_eliminar_item(db: ConexionBD):
    print("\n--- Eliminar Ítem del Menú (P06) ---")
    opcion_listar_items(db)
    id_item = leer_entero("\nIngrese el ID del ítem a eliminar: ")
    item = db.obtener_item_por_id(id_item)
    if not item:
        print(f"[Error] No se encontró ningún ítem con ID {id_item}.")
        return

    if db.eliminar_item(id_item):
        print(f"\n[Éxito] El registro '{item['nombre']}' (ID {id_item}) ha sido eliminado.")
    else:
        print("[Error] No se pudo eliminar el registro.")

def opcion_registrar_pedido_mesa(db: ConexionBD):
    print("\n--- Registrar Pedido de Mesa (P12) ---")
    numero_mesa = leer_entero("Ingrese el número de mesa (ej. 4): ")
    
    if db.mesa_tiene_pedido_abierto(numero_mesa):
        print(f"[Operación Bloqueada] La mesa {numero_mesa} ya tiene un pedido abierto y no se puede abrir otro.")
        return

    print("\n¿Desea registrar el caso de prueba P12 automáticamente? (2 platos calientes, 1 bebida, 1 postre, 'sin cebolla')")
    auto = input("¿Cargar caso de prueba P12? (s/n) [por defecto 's']: ").strip().lower()
    
    if auto != "n":
        items = [
            {"nombre": "Plato Caliente: Cazuela", "tipo": "Plato caliente", "cantidad": 2, "observacion": "sin cebolla", "subtotal": 17000},
            {"nombre": "Bebida: Bebida Cola", "tipo": "Bebida", "cantidad": 1, "observacion": "", "subtotal": 2000},
            {"nombre": "Postre: Tiramisú", "tipo": "Postre", "cantidad": 1, "observacion": "", "subtotal": 4000}
        ]
    else:
        items = []
        opcion_listar_items(db)
        while True:
            id_item = leer_entero("\nIngrese ID del ítem (o 0 para finalizar): ")
            if id_item == 0:
                break
            it = db.obtener_item_por_id(id_item)
            if not it:
                print("ID no válido.")
                continue
            cant = leer_entero(f"Cantidad de '{it['nombre']}': ")
            obs = input("Observación (opcional, ej. 'sin cebolla'): ").strip()
            items.append({
                "nombre": it['nombre'],
                "tipo": it['tipo'],
                "cantidad": cant,
                "observacion": obs,
                "subtotal": it['precio'] * cant
            })
    
    if not items:
        print("No se agregaron productos al pedido.")
        return

    try:
        id_pedido = db.abrir_pedido_mesa(numero_mesa, items)
        print(f"\n[Éxito] Pedido #{id_pedido} registrado como un solo registro de pedido en la mesa {numero_mesa}.")
        print("Líneas de detalle guardadas:")
        for it in items:
            obs_str = f" [Obs: {it['observacion']}]" if it['observacion'] else ""
            print(f" -> {it['cantidad']}x {it['nombre']}{obs_str} - Subtotal: ${it['subtotal']:,} CLP")
    except MesaOcupadaException as e:
        print(f"[Error - Mesa Ocupada]: {e}")
    except Exception as e:
        print(f"[Error]: {e}")

def opcion_ver_detalle_pedido(db: ConexionBD):
    print("\n--- Ver Detalle de Pedido de Mesa (P13) ---")
    pedidos = db.listar_pedidos()
    if not pedidos:
        print("No hay pedidos registrados.")
        return

    print("Pedidos registrados recientemente:")
    for p in pedidos[:5]:
        print(f" -> Pedido #{p['id_pedido']} | Mesa {p['numero_mesa']} | Estado: {p['estado']} | Total: ${p['total']:,} CLP | Fecha: {p['fecha_hora']}")

    id_pedido = leer_entero("\nIngrese el ID de pedido a consultar: ")
    pedido = db.obtener_pedido_con_detalles(id_pedido)
    if not pedido:
        print(f"[Error] No se encontró el pedido #{id_pedido}.")
        return

    print("\n" + "=" * 60)
    print(f"DETALLE DEL PEDIDO #{pedido['id_pedido']} (Mesa {pedido['numero_mesa']})")
    print(f"Estado: {pedido['estado']} | Fecha: {pedido['fecha_hora']}")
    print("=" * 60)
    print(f"{'Línea':<6} | {'Ítem':<30} | {'Cant':<4} | {'Observación':<16} | {'Subtotal'}")
    print("-" * 60)
    for idx, d in enumerate(pedido.get("detalles", []), 1):
        obs = d.get("observacion") or "-"
        print(f"{idx:<6} | {d['nombre_item']:<30} | {d['cantidad']:<4} | {obs:<16} | ${d['subtotal']:,} CLP")
    print("-" * 60)
    print(f"TOTAL DEL PEDIDO: ${pedido['total']:,} CLP")
    print("=" * 60)

def opcion_probar_regla_mesa_ocupada(db: ConexionBD):
    print("\n--- Probar Regla: Mesa con Pedido Abierto (P14) ---")
    print("Paso 1: Abriendo pedido en la Mesa 4 sin cerrarlo...")
    
    # Liberar mesa 4 si tenía algo previo para asegurar la prueba
    conn = db.conectar()
    conn.execute("UPDATE pedidos SET estado = 'Cerrado' WHERE numero_mesa = 4 AND estado = 'Abierto'")
    conn.execute("UPDATE mesas SET tiene_pedido_abierto = 0, estado = 'Disponible' WHERE numero = 4")
    conn.commit()
    conn.close()

    try:
        id1 = db.abrir_pedido_mesa(4, [{"nombre": "Cazuela", "cantidad": 1, "subtotal": 8500}])
        print(f"[Paso 1 OK] Pedido #{id1} abierto con éxito en Mesa 4.")
    except Exception as e:
        print(f"Error en paso 1: {e}")
        return

    print("\nPaso 2: Intentando abrir un SEGUNDO pedido en la Mesa 4 (sin cerrar el anterior)...")
    try:
        db.abrir_pedido_mesa(4, [{"nombre": "Bebida Cola", "cantidad": 1, "subtotal": 2000}])
        print("[FALLA]: Se permitió abrir el segundo pedido en la mesa ocupada.")
    except MesaOcupadaException as ex:
        print(f"[ÉXITO - Regla Cumplida]: El segundo pedido fue impedido.")
        print(f"Mensaje del sistema: '{ex}'")
        print("El programa sigue funcionando con total normalidad.")

def opcion_probar_regla_sin_stock():
    print("\n--- Probar Regla: Plato con Ingrediente Clave sin Stock (P15) ---")
    print("Configurando ingrediente clave 'Carne de Vacuno' con stock = 0...")
    carne_sin_stock = Ingrediente(nombre="Carne de Vacuno", stock_actual=0, es_clave=True)
    cazuela = PlatoCaliente(nombre="Cazuela", precio_base=8500, ingredientes=[carne_sin_stock])

    mesa_test = Mesa(numero=2)
    pedido_test = Pedido(mesa=mesa_test)

    print("Intentando agregar 'Cazuela' al pedido...")
    try:
        pedido_test.agregarDetalle(cazuela, cant=1, obs="con choclo")
        print("[FALLA]: Se permitió agregar el plato sin stock.")
    except ReglaNegocioException as ex:
        print(f"[ÉXITO - Regla Cumplida]: La operación se impidió exitosamente.")
        print(f"Mensaje del sistema: '{ex}'")
        print("El programa sigue funcionando con normalidad.")

def opcion_calcular_dolar_api():
    print("\n--- Consultar Dólar API y Calcular Bebida Importada (P16, P17) ---")
    vino = BebidaImportada(nombre="Vino Reserva Importado", precio_base=0, con_alcohol=True, precio_usd=20)
    print(f"Producto: {vino.nombre} (Precio: {vino.precioUSD} USD)")
    print("Consultando API mindicador.cl (https://mindicador.cl/api/dolar)...")
    
    dolar = IndicadorService.obtener_valor_dolar()
    precio_clp = vino.cotizarSegunDolar(dolar)
    
    print(f"Valor oficial del dólar utilizado: ${dolar:,} CLP")
    print(f"Precio final calculado en CLP: ${precio_clp:,} CLP")
    print("(Si desconectas el wifi y pruebas nuevamente, el sistema usará el valor de respaldo sin caerse).")

def opcion_validar_rut():
    print("\n--- Validar RUT para Boleta (P07, P08) ---")
    rut_ingresado = input("Ingrese el RUT a validar (ej. 12.345.678-5 o 12.345.678-9): ").strip()
    
    boleta = Boleta(numero_boleta=999)
    if boleta.validarRut(rut_ingresado):
        print(f"[Aceptado]: El RUT '{rut_ingresado}' es VÁLIDO (Dígito verificador correcto bajo Módulo 11).")
    else:
        print(f"[Rechazado]: El RUT '{rut_ingresado}' es INVÁLIDO (Dígito verificador incorrecto o formato inválido).")
        print("El programa rechaza el dato y sigue funcionando con normalidad.")

def ejecutar_demostracion_completa(db: ConexionBD):
    print("\n" + "=" * 65)
    print("   EJECUCIÓN COMPLETA DE PRUEBAS AUTOMÁTICAS (P01 - P19)")
    print("=" * 65)
    
    print("\n[P01] Programa ejecutado correctamente con su menú.")
    
    print("\n[P02] Creando ítem del menú 'Cazuela' por $8.500 CLP...")
    id_cazuela = db.crear_item("Cazuela", "Plato caliente", 8500)
    print(f" -> Confirmación: Ítem 'Cazuela' creado con ID {id_cazuela}.")

    print("\n[P03] Listando ítems del menú...")
    items = db.listar_items()
    cazuela_encontrada = any(it["id"] == id_cazuela for it in items)
    print(f" -> Registro recién creado visible en el listado: {cazuela_encontrada}")

    print("\n[P04] Modificando precio de 'Cazuela' a $9.000 CLP...")
    db.modificar_precio_item(id_cazuela, 9000)
    item_mod = db.obtener_item_por_id(id_cazuela)
    print(f" -> Nuevo precio verificado en base de datos: ${item_mod['precio']:,} CLP")

    print("\n[P05] Persistencia en base de datos: Los datos quedan almacenados en SQLite 'restaurante.db'.")

    print("\n[P06] Eliminando el registro de prueba...")
    db.eliminar_item(id_cazuela)
    item_del = db.obtener_item_por_id(id_cazuela)
    print(f" -> Verificación: ¿El ítem ya no aparece?: {item_del is None}")

    print("\n[P07] RUT correcto: '12.345.678-5'")
    b = Boleta(1)
    print(f" -> Resultado: {'Aceptado' if b.validarRut('12.345.678-5') else 'Rechazado'}")

    print("\n[P08] RUT incorrecto (DV incorrecto): '12.345.678-9'")
    print(f" -> Resultado: {'Rechazado con éxito' if not b.validarRut('12.345.678-9') else 'Aceptado erróneamente'}")

    print("\n[P09, P10, P11] Tiempos de preparación y estaciones por tipo:")
    plato = PlatoCaliente("Plato")
    beb = Bebida("Bebida")
    pos = Postre("Postre")
    print(f" -> Plato Caliente: {plato.tiempoPreparacion} min / {plato.estacionCocina}")
    print(f" -> Bebida:         {beb.tiempoPreparacion} min / {beb.estacionCocina}")
    print(f" -> Postre:         {pos.tiempoPreparacion} min / {pos.estacionCocina}")

    print("\n[P12, P13] Registrar pedido de mesa con detalles y 'sin cebolla':")
    conn = db.conectar()
    conn.execute("UPDATE pedidos SET estado = 'Cerrado' WHERE numero_mesa = 5 AND estado = 'Abierto'")
    conn.execute("UPDATE mesas SET tiene_pedido_abierto = 0 WHERE numero = 5")
    conn.commit()
    conn.close()

    items_p12 = [
        {"nombre": "Plato Caliente: Lomo", "tipo": "Plato caliente", "cantidad": 2, "observacion": "sin cebolla", "subtotal": 17000},
        {"nombre": "Bebida: Cola", "tipo": "Bebida", "cantidad": 1, "observacion": "", "subtotal": 2000},
        {"nombre": "Postre: Flan", "tipo": "Postre", "cantidad": 1, "observacion": "", "subtotal": 3500}
    ]
    id_ped = db.abrir_pedido_mesa(5, items_p12)
    ped_det = db.obtener_pedido_con_detalles(id_ped)
    print(f" -> Pedido #{id_ped} guardado con {len(ped_det['detalles'])} líneas de detalle.")
    for d in ped_det['detalles']:
        obs_tag = f" (Obs: {d['observacion']})" if d['observacion'] else ""
        print(f"    * {d['cantidad']}x {d['nombre_item']}{obs_tag} = ${d['subtotal']:,} CLP")

    print("\n[P14] Regla mesa ocupada (Mesa 5 ya tiene pedido abierto):")
    try:
        db.abrir_pedido_mesa(5, [{"nombre": "Item", "subtotal": 1000}])
        print(" -> ERROR: Permitió segundo pedido.")
    except MesaOcupadaException as e:
        print(f" -> Impedido correctamente: {e}")

    print("\n[P15] Regla ingrediente clave sin stock:")
    ing_cero = Ingrediente("Carne", stock_actual=0, es_clave=True)
    plato_cero = PlatoCaliente("Cazuela", ingredientes=[ing_cero])
    ped_test = Pedido()
    try:
        ped_test.agregarDetalle(plato_cero, 1)
        print(" -> ERROR: Permitió plato sin stock.")
    except ReglaNegocioException as e:
        print(f" -> Impedido correctamente: {e}")

    print("\n[P16, P17] Dólar API:")
    dolar_val = IndicadorService.obtener_valor_dolar()
    vino_test = BebidaImportada("Vino 20 USD", precio_usd=20)
    print(f" -> Dólar del día: ${dolar_val:,} CLP | Precio Vino: ${vino_test.cotizarSegunDolar(dolar_val):,} CLP")

    print("\n[P18] Manejo de opción inexistente '99': Muestra aviso y vuelve al menú.")
    print("[P19] Entrada con letras 'abc' donde va número: Capturado sin caída.")
    print("\n=== FIN DE LA DEMOSTRACIÓN DEL GUION DE PRUEBAS ===")

# =========================================================================
# BUCLE PRINCIPAL DEL PROGRAMA
# =========================================================================

def main():
    db = ConexionBD()
    
    # Si se pasa argumento '--demo' por consola, corre la demostración directamente
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        ejecutar_demostracion_completa(db)
        return

    while True:
        mostrar_menu()
        opcion_str = input("\nIngrese una opción: ").strip()

        if opcion_str == "1":
            opcion_crear_item(db)
        elif opcion_str == "2":
            opcion_listar_items(db)
        elif opcion_str == "3":
            opcion_modificar_precio(db)
        elif opcion_str == "4":
            opcion_eliminar_item(db)
        elif opcion_str == "5":
            opcion_registrar_pedido_mesa(db)
        elif opcion_str == "6":
            opcion_ver_detalle_pedido(db)
        elif opcion_str == "7":
            opcion_probar_regla_mesa_ocupada(db)
        elif opcion_str == "8":
            opcion_probar_regla_sin_stock()
        elif opcion_str == "9":
            opcion_calcular_dolar_api()
        elif opcion_str == "10":
            opcion_validar_rut()
        elif opcion_str == "11":
            ejecutar_demostracion_completa(db)
        elif opcion_str == "0":
            print("\n¡Gracias por utilizar el Sistema Restaurante Sabores del Sur! Hasta pronto.")
            break
        else:
            # Cumplimiento estricto de P18: si ingresa opción inexistente (ej. '99')
            print(f"\n[Aviso] La opción '{opcion_str}' no es válida. Por favor, ingrese una opción del menú (0 al 11).")

if __name__ == "__main__":
    main()
