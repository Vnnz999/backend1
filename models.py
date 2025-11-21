from db import db
from sqlalchemy import func
from datetime import datetime
from flask_login import UserMixin
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    nome= db.Column(db.String(30), unique=True)
    senha= db.Column(db.String())
    email= db.Column(db.String(120), unique=True, nullable=False)
    cpf= db.Column(db.String(11), nullable=True)
    role = db.Column(db.String(20), default='funcionario') # 'gerente' ou 'funcionario'
    cidade = db.Column(db.String(50))
    palavra_seguranca = db.Column(db.String(50)) # Para recuperar senha de admin

class Produto(db.Model):
    __tablename__ = "produtos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tamanho = db.Column(db.String(10), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    valor_compra = db.Column(db.Float)   # custo REAL
    categoria = db.Column(db.String(20), nullable=False)
    objeto = db.Column(db.String(20), nullable=False)
    movimentacoes = db.relationship("Movimentacao", backref="produto", lazy=True)

    def calcular_estoque(self):
        def safe_float(value):
            """Converte o valor para float, retornando 0.0 se for None ou uma string inválida."""
            try:
                # O valor é lido do DB como string se o tipo de DB for flexível (ex: SQLite)
                # ou como None. Tentamos converter.
                return float(value)
            except (ValueError, TypeError):
                # Se for None ou uma string como "abc", retorna 0
                return 0.0

        # Aplica safe_float para garantir que m.quantidade seja um número antes de somar
        entradas = sum(safe_float(m.quantidade) for m in self.movimentacoes if m.tipo == "entrada")
        saidas = sum(safe_float(m.quantidade) for m in self.movimentacoes if m.tipo == "saida")
        
        # O retorno é garantido como float, evitando o erro no Dashboard
        return entradas - saidas
    @property 
    def valor_total2(self):
        return self.calcular_estoque() * self.valor
    
    @property
    def custo_total_estoque(self):
        # Valor total de COMPRA (custo) do estoque
        # Se valor_compra for None, assume 0.0
        custo_unitario = self.valor_compra if self.valor_compra is not None else 0.0
        return self.calcular_estoque() * custo_unitario


    def estoque_na_data(self, data):
        entradas = db.session.query(func.sum(Movimentacao.quantidade)).filter(
            Movimentacao.produto_id == self.id,
            Movimentacao.tipo == "entrada",
            Movimentacao.data <= data
        ).scalar() or 0

        saidas = db.session.query(func.sum(Movimentacao.quantidade)).filter(
            Movimentacao.produto_id == self.id,
            Movimentacao.tipo == "saida",
            Movimentacao.data <= data
        ).scalar() or 0

        return entradas - saidas






class Movimentacao(db.Model):
    __tablename__ = "movimentacoes"
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' ou 'saida'
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quantidade = db.Column(db.Integer, nullable=False)
    estoque_apos_movimentacao = db.Column(db.Integer, nullable=False)  # novo campo
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship("Usuario") # Para saber quem foi que fez movimentação

