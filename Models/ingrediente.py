class Ingrediente:
    def __init__(self, nombre: str, stock_actual: int = 0, es_clave: bool = False):
        self.nombre = nombre
        self.stockActual = stock_actual
        self.esClave = es_clave

    def tieneStockSuficiente(self, cantidad_necesaria: int = 1) -> bool:
        return self.stockActual >= cantidad_necesaria

    def descontarStock(self, cantidad: int) -> bool:
        if self.tieneStockSuficiente(cantidad):
            self.stockActual -= cantidad
            return True
        return False

    def __str__(self):
        return f"Ingrediente {self.nombre} (Stock: {self.stockActual}, Clave: {self.esClave})"
