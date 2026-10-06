class NaoEncontrado(Exception):
    """ O recurso pedido não existe. Vira 404. """

class Conflito(Exception):
    """A operação quebraria uma regra de unicidade ou um vínculo. Vira 409."""

class RegraDeNegocio(Exception):
    """Os dados são válidos no formato, mas a regra da loja não deixa. Vira 400"""

class NaoAutenticado(Exception):
    """Token ausente, inválido ou expirado, ou login incorreto. Vira 401."""

class SemPermissao(Exception):
    """O usuário está logado, mas o papel dele não permite a ação. Vira 403."""
