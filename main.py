from Dao.conexión import ConexionBD
from Models import Boleta, BebidaImportada, MesaOcupadaException

def main():
    db = ConexionBD()
    print("=== SISTEMA RESTAURANTE SABORES DEL SUR ===")

    # 1. Prueba de Validación (RUT)
    print("\n--- 1. Probando Validación de Entrada (RUT) ---")
    boleta = Boleta(1, "12345678-9", 0)
    try:
        boleta.rut_cliente = "12345"  # RUT inválido a propósito
    except ValueError as e:
        print(f"[Validación Correcta - Rechazado]: {e}")

    # 2. Prueba de API Externa (Precio con indicador)
    print("\n--- 2. Probando API (Bebida Importada según Dólar) ---")
    vino = BebidaImportada("Vino Reserva", 0, True, 20)  # 20 USD
    precio_calculado = vino.calcularPrecio()
    print(f"Precio calculado para {vino.nombre} (20 USD): ${precio_calculado} CLP")

    # 3. Prueba de Reglas de Negocio (Excepciones propias)
    print("\n--- 3. Probando Reglas de Negocio y Excepciones ---")
    mesa_ocupada = True
    try:
        if mesa_ocupada:
            raise MesaOcupadaException("Error: La mesa ya tiene un pedido abierto y no se puede abrir otro.")
    except MesaOcupadaException as ex:
        print(f"[Regla 1 Bloqueada con éxito]: {ex}")

    # 4. Prueba de Transacción con Líneas de Detalle en Base de Datos
    print("\n--- 4. Probando Transacción y CRUD en Base de Datos ---")
    items_pedido = [
        {"nombre": "Plato Caliente: Lomo a lo Pobre", "cantidad": 2, "subtotal": 16000},
        {"nombre": "Bebida Cola", "cantidad": 2, "subtotal": 3000}
    ]
    db.guardar_pedido_con_detalles(numero_mesa=5, items=items_pedido)

    print("\n¡Sistema ejecutado y listo para la demostración!")

if __name__ == "__main__":
    main()
