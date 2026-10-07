# Restaurante Sabores del Sur 🍽️

Sistema de gestión para el restaurante **"Sabores del Sur"**, implementado en Python siguiendo una arquitectura en capas (DAO, Modelos y Servicios) y el modelo de referencia UML del proyecto.

**Equipo:** Elías Barraza & Patricia Magaña  
**Asignatura / Contexto:** ES1 TI3V21 114-2A-F2

---

## 📋 Descripción del Proyecto

El sistema gestiona el ciclo operativo de atención en el restaurante: asignación y estado de mesas, toma de pedidos por meseros, preparación en cocina según estación, cálculo polimórfico de precios (incluyendo cotización en tiempo real de bebidas importadas según el tipo de cambio oficial) y persistencia transaccional de pedidos en base de datos SQLite.

---

## 🏛️ Arquitectura del Sistema

```text
Restaurant.py/
├── Dao/
│   ├── __init__.py
│   └── conexión.py             # Conexión SQLite, DDL de tablas y transacciones parametrizadas
├── Models/
│   ├── __init__.py
│   ├── boleta.py               # Emisión de boleta y validación de formato RUT
│   ├── excepciones.py          # Excepciones propias de reglas de negocio (MesaOcupadaException)
│   ├── ingrediente.py          # Control de stock de insumos
│   ├── item_menu.py            # ItemMenu y polimorfismo (PlatoCaliente, Bebida, BebidaImportada, Postre)
│   ├── mesa.py                 # Gestión de estado de mesas y pedidos abiertos
│   ├── pedido.py               # Transacciones de pedidos y líneas de detalle (DetallePedido)
│   └── trabajador.py           # Jerarquía de Trabajador, Mesero y Cocinero
├── Services/
│   ├── __init__.py
│   └── indicador_service.py    # Integración con API externa (mindicador.cl) para el dólar observado
├── main.py                     # Demostración del flujo y pruebas de validación
└── README.md
```

---

## 🚀 Características y Reglas de Negocio

1. **Polimorfismo en Items de Menú**:
   - Sobrescritura de `calcularPrecio()` en subtipos: `PlatoCaliente`, `Bebida`, `BebidaImportada` y `Postre`.
   - `BebidaImportada` cotiza su valor en CLP en función del dólar del día (`cotizarSegunDolar()`).

2. **Integración con API Externa**:
   - Consulta del tipo de cambio oficial del dólar estadounidense a través de `mindicador.cl` con manejo de fallback en caso de indisponibilidad.

3. **Validación de Datos (RUT)**:
   - Control de entrada y formato de RUT en `Boleta`, rechazando entradas no válidas mediante excepciones `ValueError`.

4. **Reglas de Negocio y Excepciones Propias**:
   - Bloqueo de apertura de pedidos si la mesa ya posee uno abierto mediante `MesaOcupadaException`.

5. **Persistencia y Seguridad (DAO)**:
   - Base de datos relacional SQLite (`restaurante.db`).
   - Consultas parametrizadas que mitigan riesgos de inyección SQL.
   - Manejo de transacciones con `commit` y `rollback` en caso de error.

---

## ▶️ Ejecución de la Demostración

Para ejecutar el flujo de prueba completo:

```bash
python main.py
```

El script demostrará automáticamente:
- **Prueba 1:** Validación y rechazo de RUT inválido.
- **Prueba 2:** Consulta de API y cálculo dinámico de precio para bebida importada.
- **Prueba 3:** Bloqueo de mesa ocupada mediante excepción de regla de negocio.
- **Prueba 4:** Guardado transaccional del pedido con detalles en la base de datos.
