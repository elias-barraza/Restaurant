from typing import List
from .ingrediente import Ingrediente
from Services.indicador_service import IndicadorService

class ItemMenu:
    def __init__(self, nombre: str, precio_base: int = 0, tiempo_preparacion: int = 0, estacion_cocina: str = "General", ingredientes: List[Ingrediente] = None):
        self.nombre = nombre
        self.precioBase = precio_base
        self.tiempoPreparacion = tiempo_preparacion
        self.estacionCocina = estacion_cocina
        self.ingredientes = ingredientes if ingredientes is not None else []

    def verificarStockIngredientes(self) -> bool:
        if not self.ingredientes:
            return True
        return all(ing.tieneStockSuficiente() for ing in self.ingredientes)

    def obtenerTiempoPreparacion(self) -> int:
        return self.tiempoPreparacion

    def obtenerEstacionCocina(self) -> str:
        return self.estacionCocina

    def tratarPedido(self) -> bool:
        return self.verificarStockIngredientes()

    def calcularPrecio(self) -> int:
        return self.precioBase

    def __str__(self):
        return f"{self.nombre} - ${self.calcularPrecio()} CLP"


class PlatoCaliente(ItemMenu):
    def __init__(self, nombre: str, precio_base: int = 0, tiempo_preparacion: int = 25, ingredientes: List[Ingrediente] = None):
        super().__init__(nombre=nombre, precio_base=precio_base, tiempo_preparacion=tiempo_preparacion, estacion_cocina="Cocina Caliente", ingredientes=ingredientes)

    def calcularPrecio(self) -> int:
        # Polimorfismo: retorna el precio base del plato caliente
        return self.precioBase


class Bebida(ItemMenu):
    def __init__(self, nombre: str, precio_base: int = 0, con_alcohol: bool = False, tiempo_preparacion: int = 5, ingredientes: List[Ingrediente] = None):
        super().__init__(nombre=nombre, precio_base=precio_base, tiempo_preparacion=tiempo_preparacion, estacion_cocina="Bar", ingredientes=ingredientes)
        self.conAlcohol = con_alcohol

    def calcularPrecio(self) -> int:
        # Polimorfismo: retorna el precio base de la bebida
        return self.precioBase


class BebidaImportada(Bebida):
    def __init__(self, nombre: str, precio_base: int = 0, con_alcohol: bool = True, precio_usd: int = 0, tiempo_preparacion: int = 5, ingredientes: List[Ingrediente] = None):
        super().__init__(nombre=nombre, precio_base=precio_base, con_alcohol=con_alcohol, tiempo_preparacion=tiempo_preparacion, ingredientes=ingredientes)
        self.precioUSD = precio_usd

    def cotizarSegunDolar(self, valorDolarDia: int) -> int:
        return int(round(self.precioUSD * valorDolarDia)) + self.precioBase

    def calcularPrecio(self) -> int:
        # Polimorfismo: consulta el valor del dólar en la API y cotiza en CLP
        dolar_actual = IndicadorService.obtener_valor_dolar()
        return self.cotizarSegunDolar(dolar_actual)


class Postre(ItemMenu):
    def __init__(self, nombre: str, precio_base: int = 0, tiempo_preparacion: int = 10, ingredientes: List[Ingrediente] = None):
        super().__init__(nombre=nombre, precio_base=precio_base, tiempo_preparacion=tiempo_preparacion, estacion_cocina="Pastelería", ingredientes=ingredientes)

    def calcularPrecio(self) -> int:
        # Polimorfismo: retorna el precio base del postre
        return self.precioBase
