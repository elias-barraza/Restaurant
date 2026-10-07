from .excepciones import MesaOcupadaException

class Mesa:
    def __init__(self, numero: int, estado: str = "Disponible", tiene_pedido_abierto: bool = False):
        self.numero = numero
        self.estado = estado
        self.tienePedidoAbierto = tiene_pedido_abierto

    def verificarPedidoAbierto(self) -> bool:
        return self.tienePedidoAbierto

    def abrirMesa(self) -> bool:
        if self.tienePedidoAbierto:
            raise MesaOcupadaException(f"Error: La mesa {self.numero} ya tiene un pedido abierto y no se puede abrir otro.")
        self.tienePedidoAbierto = True
        self.estado = "Ocupada"
        return True

    def cerrarMesa(self) -> bool:
        self.tienePedidoAbierto = False
        self.estado = "Disponible"
        return True

    def __str__(self):
        return f"Mesa {self.numero} [{self.estado}] - Pedido Abierto: {self.tienePedidoAbierto}"
