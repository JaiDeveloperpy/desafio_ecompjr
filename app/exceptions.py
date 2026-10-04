class NaoEncontrado(Exception):
    """ O recurso pedido não existe. Vira 404. """

class Conflito(Exception):
    """A operação quebraria uma regra de unicidade ou um vínculo. Vira 409."""

class RegraDeNegocio(Exception):
    """Os dados são válidos no formato, mas a regra da loja não deixa. Vira 400"""