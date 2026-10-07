class MesaOcupadaException(Exception):
    """Excepción lanzada cuando una mesa ya tiene un pedido abierto y se intenta abrir otro."""
    pass

class ReglaNegocioException(Exception):
    """Excepción genérica para violaciones de reglas de negocio en el restaurante."""
    pass
