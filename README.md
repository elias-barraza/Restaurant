# Restaurante Sabores del Sur 🍽️

Sistema de gestión para el restaurante **"Sabores del Sur"**, implementado en Python bajo arquitectura en capas (DAO, Modelos y Servicios) y diseñado para satisfacer la totalidad de los requisitos del **Guión de Pruebas** del proyecto.

* **Sección:** 114-2A-F2  
* **Equipo:** Elías Barraza y Patricia Magaña  
* **Tipos de Menú:** Plato caliente / Bebida / Postre  
* **Indicador Económico:** Dólar observado ([mindicador.cl](https://mindicador.cl/api/dolar))  
* **Repositorio:** [https://github.com/elias-barraza/Restaurant](https://github.com/elias-barraza/Restaurant)

---

## 📋 Estructura del Proyecto

```text
Restaurant.py/
├── Dao/
│   ├── __init__.py
│   └── conexión.py             # SQLite, DDL de tablas (mesas, items_menu, pedidos, detalle_pedidos) y CRUD
├── Models/
│   ├── __init__.py
│   ├── boleta.py               # Emisión de boleta y validación Módulo 11 de RUT
│   ├── excepciones.py          # Excepciones propias (MesaOcupadaException, ReglaNegocioException)
│   ├── ingrediente.py          # Control de stock de insumos y verificación de clave
│   ├── item_menu.py            # ItemMenu, PlatoCaliente, Bebida, BebidaImportada, Postre
│   ├── mesa.py                 # Gestión de mesas y estados
│   ├── pedido.py               # Transacciones de pedidos y líneas de detalle con observaciones
│   └── trabajador.py           # Jerarquía de Trabajador, Mesero y Cocinero
├── Services/
│   ├── __init__.py
│   └── indicador_service.py    # Integración con API mindicador.cl (Dólar observado) con fallback
├── main.py                     # Menú interactivo de consola y suite de pruebas guiadas
├── requirements.txt            # Declaración de dependencias (biblioteca estándar)
├── .gitignore                  # Exclusión de archivos binarios, base de datos y cache
└── README.md                   # Documentación completa del sistema
```

---

## 🚀 Instalación y Ejecución (P01)

1. **Instalar dependencias declaradas en `requirements.txt`:**
   ```bash
   pip install -r requirements.txt
   ```
   *(El proyecto utiliza la biblioteca estándar de Python 3: `sqlite3`, `urllib`, `json`, `re`, `datetime`).*

2. **Iniciar la aplicación:**
   ```bash
   python main.py
   ```
   El programa iniciará de inmediato y presentará el menú interactivo principal.

3. *(Opcional)* **Ejecución automática de pruebas del guión:**
   ```bash
   python main.py --demo
   ```

---

## 🧪 Matriz de Cumplimiento: Guión de Pruebas (P01 - P19)

| N° | Prueba | Paso / Dato de prueba | Resultado en el Sistema |
|---|---|---|---|
| **P01** | **El programa se ejecuta** | Instalar `requirements.txt` y correr `main.py` | Inicia y despliega el menú interactivo. |
| **P02** | **Crear ítem del menú** | Plato "Cazuela", precio $8.500 (Opción 1) | Confirma guardado en BD con ID, tiempo y estación asignados. |
| **P03** | **Listar ítem del menú** | Solicitar listado (Opción 2) | Muestra el registro recién creado con todos sus atributos. |
| **P04** | **Modificar ítem del menú** | Cambiar precio a $9.000 y listar (Opción 3) | Actualiza el registro en la BD y el listado refleja $9.000. |
| **P05** | **Los datos quedan guardados** | Salir, reabrir el programa y listar | Los registros persisten intactos en SQLite (`restaurante.db`). |
| **P06** | **Eliminar ítem del menú** | Eliminar ítem y listar (Opción 4) | El registro se elimina de la base de datos y ya no figura. |
| **P07** | **RUT para boleta: Correcto** | Ingresar `12.345.678-5` (Opción 10) | El algoritmo Módulo 11 lo valida y el sistema lo acepta. |
| **P08** | **RUT para boleta: Incorrecto** | Ingresar `12.345.678-9` (Opción 10) | Detecta DV incorrecto, lo rechaza y el programa sigue en ejecución. |
| **P09** | **Tipo Plato Caliente** | Crear / consultar Plato Caliente | Asigna automáticamente 25 min de preparación y estación "Cocina Caliente". |
| **P10** | **Tipo Bebida** | Crear / consultar Bebida | Asigna automáticamente 5 min de preparación y estación "Bar". |
| **P11** | **Tipo Postre** | Crear / consultar Postre | Asigna automáticamente 10 min de preparación y estación "Pastelería". |
| **P12** | **Registrar pedido de mesa** | 2 platos calientes, 1 bebida, 1 postre, con observación "sin cebolla" (Opción 5) | Queda guardado como un solo registro de pedido en la BD con todas sus líneas. |
| **P13** | **Ver detalle pedido de mesa** | Consultar pedido registrado (Opción 6) | Muestra todas las líneas de detalle con su cantidad, subtotal y observación. |
| **P14** | **Regla: Mesa con pedido abierto** | Mesa 4 abierta: intentar abrir segundo pedido (Opción 7) | Lanza `MesaOcupadaException`, bloquea la apertura y el programa continúa. |
| **P15** | **Regla: Ingrediente sin stock** | Dejar stock = 0 en ingrediente clave e intentar pedirlo (Opción 8) | Lanza `ReglaNegocioException`, impide la adición y el programa continúa. |
| **P16** | **Precio con dólar del día** | Calcular vinos importados con internet (Opción 9) | Consulta `https://mindicador.cl/api/dolar` y calcula en CLP con el valor oficial. |
| **P17** | **Sin internet** | Desconectar wifi y calcular precio (Opción 9) | Captura la excepción, avisa uso de valor fallback ($950 CLP) y no se cae. |
| **P18** | **Opción inexistente** | Ingresar opción `99` en el menú | Despliega mensaje de opción no válida y vuelve al menú sin fallar. |
| **P19** | **Letras donde va número** | Escribir `abc` en campo numérico de precio/cantidad | Informa error de tipo y vuelve a solicitar el valor sin caerse. |
