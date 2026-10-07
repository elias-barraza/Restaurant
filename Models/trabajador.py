class Trabajador:
    def __init__(self, rut: str = "", nombre: str = "", rol: str = ""):
        self.rut = rut
        self.nombre = nombre
        self.rol = rol

    def __str__(self):
        return f"{self.rol}: {self.nombre} (RUT: {self.rut})"


class Mesero(Trabajador):
    def __init__(self, rut: str = "", nombre: str = ""):
        super().__init__(rut=rut, nombre=nombre, rol="Mesero")

    def tomarPedido(self, mesa):
        from .pedido import Pedido
        return Pedido(mesa=mesa, mesero=self)

    def marcarMesa(self, mesa, estado: str) -> bool:
        if mesa:
            mesa.estado = estado
            return True
        return False


class Cocinero(Trabajador):
    def __init__(self, rut: str = "", nombre: str = "", estacion_asignada: str = "Cocina Caliente"):
        super().__init__(rut=rut, nombre=nombre, rol="Cocinero")
        self.estacionAsignada = estacion_asignada

    def prepararPlato(self, detalle) -> bool:
        print(f"[Cocinero {self.nombre}] Preparando {detalle.itemMenu.nombre} en estación {self.estacionAsignada}.")
        return True

    def marcarListo(self, detalle) -> bool:
        if detalle:
            return detalle.marcarComoListo()
        return False
