from datetime import datetime
from typing import List, Optional
from .item_menu import ItemMenu
from .mesa import Mesa
from .trabajador import Mesero
from .boleta import Boleta

class DetallePedido:
    def __init__(self, item_menu: ItemMenu, cantidad: int = 1, observacion: str = "", esta_listo: bool = False):
        self.itemMenu = item_menu
        self.cantidad = cantidad
        self.observacion = observacion
        self.estaListo = esta_listo

    def marcarComoListo(self) -> bool:
        self.estaListo = True
        return True

    def calcularSubtotal(self) -> int:
        return self.itemMenu.calcularPrecio() * self.cantidad

    def __str__(self):
        estado = "Listo" if self.estaListo else "En Preparación"
        return f"{self.cantidad}x {self.itemMenu.nombre} - Subtotal: ${self.calcularSubtotal()} ({estado})"


class Pedido:
    _contador_pedidos = 1

    def __init__(
        self,
        numero_pedido: Optional[int] = None,
        mesa: Optional[Mesa] = None,
        mesero: Optional[Mesero] = None,
        boleta: Optional[Boleta] = None,
        estado: str = "Abierto"
    ):
        if numero_pedido is None:
            self.numeroPedido = Pedido._contador_pedidos
            Pedido._contador_pedidos += 1
        else:
            self.numeroPedido = numero_pedido

        self.fechaHora = datetime.now()
        self.estado = estado
        self.mesa = mesa
        self.mesero = mesero
        self.boleta = boleta
        self.detalles: List[DetallePedido] = []

        if self.mesa:
            self.mesa.abrirMesa()

    def agregarDetalle(self, item: ItemMenu, cant: int, obs: str = "") -> bool:
        if self.estado != "Abierto":
            print(f"[Pedido #{self.numeroPedido}] No se pueden agregar items a un pedido cerrado.")
            return False
        detalle = DetallePedido(item_menu=item, cantidad=cant, observacion=obs)
        self.detalles.append(detalle)
        return True

    def calcularTotal(self) -> int:
        return sum(d.calcularSubtotal() for d in self.detalles)

    def cerrarPedido(self) -> bool:
        self.estado = "Cerrado"
        if self.mesa:
            self.mesa.cerrarMesa()
        total = self.calcularTotal()
        if not self.boleta:
            self.boleta = Boleta(numero_boleta=self.numeroPedido, rut_cliente="66666666-6", monto_total=total)
        else:
            self.boleta.montoTotal = total
        self.boleta.emitirDocumento()
        return True

    def __str__(self):
        return f"Pedido #{self.numeroPedido} [Mesa: {self.mesa.numero if self.mesa else 'N/A'}] - Total: ${self.calcularTotal()}"
