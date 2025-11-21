from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from views import *
from models import Usuario, Produto, Movimentacao
from db import db
import hashlib
from flask_migrate import Migrate
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import random
#from templates.estoque import estoque_bp
from sqlalchemy import func
from datetime import datetime, timedelta
from sqlalchemy import extract, desc
import pdfkit
import os



app = Flask(__name__)
app.secret_key = 'admim'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# Formato: mysql+pymysql://USUARIO:SENHA@HOST/NOME_DO_BANCO
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:vinicouter1@localhost/impacto_multimarcas'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def hash(txt):
   hash_obj = hashlib.sha256(txt.encode('utf-8'))
   return hash_obj.hexdigest()


lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


def validar_email(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email) is not None

@lm.user_loader
def user_loader(id):
   usuario = db.session.query(Usuario).filter_by(id=id).first()
   return usuario

#@app.route('/')
#@login_required
#def home():
#   print('usuario:', current_user.nome)
#   return render_template('home.html', usuario=current_user)
   


@app.route('/')
@login_required
def home():
    agora = datetime.now()
    mes = agora.month
    ano = agora.year

    # Soma das ENTRADAS no mês
    entradas = db.session.query(func.sum(Movimentacao.quantidade)).filter(
        Movimentacao.tipo == "entrada",
        extract('month', Movimentacao.data) == mes,
        extract('year', Movimentacao.data) == ano
    ).scalar() or 0

    # Soma das SAÍDAS no mês
    saidas = db.session.query(func.sum(Movimentacao.quantidade)).filter(
        Movimentacao.tipo == "saida",
        extract('month', Movimentacao.data) == mes,
        extract('year', Movimentacao.data) == ano
    ).scalar() or 0

    # ❗ VENDAS POR CATEGORIA (somando quantidade das SAÍDAS)
    categorias = db.session.query(
        Produto.categoria,
        func.sum(Movimentacao.quantidade)
    ).join(Movimentacao, Movimentacao.produto_id == Produto.id)\
    .filter(
        Movimentacao.tipo == "saida",
        extract('month', Movimentacao.data) == mes,
        extract('year', Movimentacao.data) == ano
    )\
    .group_by(Produto.categoria)\
    .all()

    categorias_labels = [c[0] for c in categorias]
    categorias_quantidades = [int(c[1]) for c in categorias]

    print('usuario:', current_user.nome)
    objetos = ['Camisa', 'Calça', 'Bermuda']
    tamanhos_por_objeto = {
        'Camisa': ['PP', 'P', 'M', 'G', 'GG'],
        'Calça': ['36', '38', '40', '42'],
        'Bermuda': ['36', '38', '40', '42']
    }

    objeto_selecionado = request.args.get('objeto', None)  # None em vez de ''
    tamanhos_disponiveis = tamanhos_por_objeto.get(objeto_selecionado, [])
    movimentacoes = Movimentacao.query.order_by(Movimentacao.data.desc()).all()
    produtos = Produto.query.all()  # <-- ADICIONE ISSO
    total_produtos=Produto.query.count()
    valor_total = db.session.query(func.sum(Produto.valor)).scalar() or 0
    total_estoque = sum(produto.calcular_estoque() for produto in produtos)
    valor_total2 = sum(produto.valor_total2 for produto in produtos)
    custo_total_estoque = sum(produto.custo_total_estoque for produto in produtos)
    estoque_baixo = [produto for produto in produtos if produto.calcular_estoque() < 10]
    quantidade_produtos_baixo_estoque = len(estoque_baixo)
    usuarios_lista = Usuario.query.all()

    return render_template(
        'home.html',
        entradas=int(entradas),
        saidas=int(saidas),
        categorias_labels=categorias_labels,
        categorias_quantidades=categorias_quantidades,
        usuario=current_user,
        produtos=produtos, 
        total_produtos=total_produtos,
        valor_total=valor_total,
        objetos=objetos,  # <-- não esqueça de passar isso
        objeto_selecionado=objeto_selecionado,
        tamanhos=tamanhos_disponiveis,
        total_estoque=total_estoque,
        valor_total2=valor_total2,
        estoque_baixo=estoque_baixo,
        quantidade_produtos_baixo_estoque=quantidade_produtos_baixo_estoque,
        movimentacoes=movimentacoes,
        custo_total_estoque=custo_total_estoque, # Se for o Custo Total
        usuarios=usuarios_lista # <--- ENVIA A LISTA PRO HTML
    )






@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method =='GET':
        return render_template('login.html')
        
    elif request.method =='POST':
        nome = request.form['usuarioForm']
        senha = request.form['senhaForm']

        user = db.session.query(Usuario).filter_by(nome=nome).first()
        
        if not user or not check_password_hash(user.senha, senha):
            session.pop('_flashes', None)
            flash('Nome ou senha incorretos.', 'danger')
            return redirect(url_for('login'))
 
        login_user(user)
        flash(f'Bem-vindo, {user.nome}!', 'success')

        # --- MUDANÇA AQUI: LÓGICA DE REDIRECIONAMENTO POR CARGO ---
        # Se for gerente -> Home completa
        # Se for outro -> Tela de funcionário
        if hasattr(user, 'role') and user.role == 'gerente':
            return redirect(url_for('home')) 
        else:
            return redirect(url_for('funcionario'))
        

@app.route('/funcionario')
@login_required
def funcionario():
    # 1. Buscar dados para os Gráficos (Igual à Home)
    agora = datetime.now()
    mes = agora.month
    ano = agora.year

    entradas = db.session.query(func.sum(Movimentacao.quantidade)).filter(
        Movimentacao.tipo == "entrada",
        extract('month', Movimentacao.data) == mes,
        extract('year', Movimentacao.data) == ano
    ).scalar() or 0

    saidas = db.session.query(func.sum(Movimentacao.quantidade)).filter(
        Movimentacao.tipo == "saida",
        extract('month', Movimentacao.data) == mes,
        extract('year', Movimentacao.data) == ano
    ).scalar() or 0

    categorias = db.session.query(
        Produto.categoria,
        func.sum(Movimentacao.quantidade)
    ).join(Movimentacao, Movimentacao.produto_id == Produto.id)\
    .filter(
        Movimentacao.tipo == "saida",
        extract('month', Movimentacao.data) == mes,
        extract('year', Movimentacao.data) == ano
    )\
    .group_by(Produto.categoria)\
    .all()

    categorias_labels = [c[0] for c in categorias]
    categorias_quantidades = [int(c[1]) for c in categorias]

    # 2. Buscar Produtos e Movimentações
    produtos = Produto.query.all()
    movimentacoes = Movimentacao.query.order_by(Movimentacao.data.desc()).all()

    # 3. Calcular Totais do Dashboard
    total_estoque = sum(produto.calcular_estoque() for produto in produtos)
    valor_total2 = sum(produto.valor_total2 for produto in produtos)
    
    estoque_baixo = [produto for produto in produtos if produto.calcular_estoque() < 10]
    quantidade_produtos_baixo_estoque = len(estoque_baixo)

    # --- PACOTE DE DADOS (Para não repetir no return) ---
    dados_para_o_html = {
        'usuario': current_user,
        'produtos': produtos,
        'movimentacoes': movimentacoes,
        'total_estoque': total_estoque,
        'valor_total2': valor_total2,
        'quantidade_produtos_baixo_estoque': quantidade_produtos_baixo_estoque,
        'entradas': int(entradas),
        'saidas': int(saidas),
        'categorias_labels': categorias_labels,
        'categorias_quantidades': categorias_quantidades
    }

    # --- LÓGICA DE DETECÇÃO MOBILE ---
    user_agent = request.user_agent.string.lower()
    mobile_tokens = ['android', 'iphone', 'ipod', 'mobile', 'webos']
    
    # Verifica se é celular
    is_mobile = any(token in user_agent for token in mobile_tokens)

    if is_mobile:
        # Carrega o HTML novo (salve o código anterior como funcionario_mobile.html)
        return render_template('funcionario_mobile.html', **dados_para_o_html)
    else:
        # Carrega o HTML antigo (Desktop)
        return render_template('funcionario.html', **dados_para_o_html)


#aba de registrar, nome, valida email senha e coleta as informações
#@app.route('/registrar', methods=['GET', 'POST'])
#def registrar():
    #if request.method =='GET':
        #return render_template('registrar.html')
    
    #elif request.method == 'POST':
       #nome = request.form['usuarioForm']

       #cpf = request.form['cpfForm']
       #cpf_numeros = ''.join(filter(str.isdigit, cpf))
       #if len(cpf_numeros) != 11:
        #flash('O CPF deve ter exatamente 11 caracteres.', 'danger')
        #return redirect(url_for('registrar'))
       
       #email = request.form['emailForm']
       #if not validar_email(email):
        #flash('Email inválido.', 'danger')
        #return redirect(url_for('registrar'))
       
       #senha = request.form['senhaForm']
       #if len(senha) < 6:
        #flash('A senha deve ter no mínimo 6 caracteres.', 'danger')
        #return redirect(url_for('registrar'))
    
       #senha_mestre = request.form['senhaMestreForm']
       #SENHA_MESTRE = 'adm'
      # if senha_mestre  != SENHA_MESTRE:
       # flash('Senha mestre incorreta. Cadastro não autorizado.', 'danger')
       # return redirect(url_for('registrar'))


    # Verifica se o usuário ja existe
    #existente = db.session.query(Usuario).filter_by(nome=nome).first()
   # if existente:
       # flash('Nome de usuário já existe. Escolha outro.', 'danger')
      #  return redirect(url_for('registrar'))



    #novo_usuario = Usuario(nome=nome, senha=hash(senha), email=email, cpf=cpf)
   # novo_usuario = Usuario(nome=nome, senha=generate_password_hash(senha), email=email, cpf=cpf)
   # db.session.add(novo_usuario)
   # db.session.commit()
 
   # login_user(novo_usuario)
   # flash('Conta criada com sucesso!', 'success')
   # return redirect(url_for('login'))


#metodo de logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("Você saiu da conta.", "info")
    return redirect(url_for('login', logout=1))


#metodo para redefinir a senha
@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        cpf = request.form.get('cpf')

        # Remove pontos e traços do CPF
        cpf_numeros = ''.join(filter(str.isdigit, cpf))

        # Procura usuario no banco
        usuario = Usuario.query.filter_by(nome=nome, email=email, cpf=cpf_numeros).first()

        if not usuario:
            flash('Usuário não encontrado ou dados incorretos.', 'danger')
            return redirect(url_for('recuperar'))

        # Dados conferem = redireciona para redefinir senha
        return redirect(url_for('redefinir', usuario_id=usuario.id))

    return render_template('recuperar.html')

#rota para redefinir a senha em outra aba
@app.route('/resetar_senha_segura', methods=['POST'])
def resetar_senha_segura():
    # 1. Coleta dos dados do formulário
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    cidade = request.form.get('cidade')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')

    # 2. Validação básica de senha
    if nova_senha != confirmar_senha:
        flash('As novas senhas não coincidem.', 'error')
        # Redirecionar para a mesma página (ou para a home, se for um reset de senha de login)
        return redirect(url_for('funcionario')) 

    # 3. Busca e validação do usuário com base nos dados seguros
    usuario = Usuario.query.filter_by(
        nome=nome, 
        cpf=cpf, 
        cidade=cidade
    ).first()

    if not usuario:
        flash('Dados de verificação incorretos. Usuário, CPF ou Cidade não correspondem.', 'error')
        return redirect(url_for('funcionario')) 

    # 4. Atualiza a senha no banco de dados
    # *AVISO: Use SEMPRE o hash para salvar a senha*
    usuario.senha = generate_password_hash(nova_senha)
    db.session.commit()
    
    # 5. Sucesso e redirecionamento
    flash('Sua senha foi redefinida com sucesso! Por favor, faça login.', 'success')
    return redirect(url_for('login')) # Redirecionar para a página de login



#-------------------------------------------------------------------------
#rotas de vendedores e gerente PRECISA CRIAR AS ROTAS AINDA NO LOGIN para acessar vend or gerent
#@app.route('/home_vendedor')
#@login_required
#def home_vendedor():
    #if current_user.role != 'vendedor':
        #flash("Acesso negado!", "danger")
        #return redirect(url_for('home_gerente'))
    #return render_template('home_vendedor.html', usuario=current_user)

#@app.route('/home_gerente')
#@login_required
#def home_gerente():
    #if current_user.role != 'gerente':
        #flash("Acesso negado!", "danger")
        #return redirect(url_for('home_vendedor'))
    #return render_template('home_gerente.html', usuario=current_user)
#---------------------------------------------------------------

#estoque ------------------------------------

#LISTAR produto
@app.route('/estoque')
@login_required
def listar_produtos():
    estoque = Produto.query.all()
    return render_template('estoque/listar.html', estoque=estoque)


#cadastrar produto
@app.route('/estoque/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        tamanho = request.form['tamanho']
        valor = request.form['valor']
        categoria = request.form['categoria']
        objeto = request.form['objeto']
        quantidade_inicial = int(request.form.get('quantidade', 0))  # pega a quantidade inicial

        # Cria o produto
        novo = Produto(nome=nome, tamanho=tamanho, valor=valor, categoria=categoria, objeto=objeto)
        db.session.add(novo)
        db.session.commit()  # necessário para ter o novo.id

        # Cria movimentação de entrada caso quantidade inicial > 0
        if quantidade_inicial > 0:
            mov = Movimentacao(
                produto_id=novo.id,
                tipo='entrada',
                quantidade=quantidade_inicial,
                data=datetime.utcnow(),
                estoque_apos_movimentacao=quantidade_inicial  # estoque inicial

            )
            db.session.add(mov)
            db.session.commit()

        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('home'))

    # GET request
    produtos = Produto.query.all()
    total_produtos = Produto.query.count()
    valor_total = db.session.query(func.sum(Produto.valor)).scalar() or 0

    return render_template(
        'home.html',
        usuario=current_user,
        produtos=produtos,
        total_produtos=total_produtos,
        valor_total=valor_total,
        valor_compra=valor     # ✅ Produto.valor_compra = Custo (Correto para cálculo)
    )




#aparecer tamanhos diferentes calça e camisa 
@app.route('/produto-form', methods=['GET', 'POST'])
@login_required
def produto_form():
    objetos = ['Camisa', 'Calça', 'Bermuda']
    tamanhos_por_objeto = {
        'Camisa': ['PP', 'P', 'M', 'G', 'GG'],
        'Calça': ['36', '38', '40', '42'],
        'Bermuda': ['PP', 'P', 'M', 'G']
    }

    objeto_selecionado = request.args.get('objeto', None)  # None em vez de ''
    tamanhos_disponiveis = tamanhos_por_objeto.get(objeto_selecionado, [])
    produtos = Produto.query.all()
    total_produtos = Produto.query.count()
    valor_total = db.session.query(func.sum(Produto.valor)).scalar() or 0

    if request.method == 'POST':
        nome = request.form.get('nome')
        tamanho = request.form.get('tamanho')
        valor = request.form.get('valor')
        categoria = request.form.get('categoria')
        objeto = request.form.get('objeto')

        if nome and tamanho and objeto:
            novo = Produto(nome=nome, tamanho=tamanho, valor=valor, categoria=categoria, objeto=objeto)
            db.session.add(novo)
            db.session.commit()
            flash(f"Produto {nome} ({objeto} {tamanho}) cadastrado com sucesso!", "success")
            return redirect(url_for('produto_form'))

    return render_template(
        'home.html',
        usuario=current_user,
        produtos=produtos,
        total_produtos=total_produtos,
        valor_total=valor_total,
        objetos=objetos,
        objeto_selecionado=objeto_selecionado,
        tamanhos=tamanhos_disponiveis
    )






#editar produto
@app.route('/estoque/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    # Busca o produto ou dá erro 404 se não existir
    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':
        # Atualiza os campos normais
        produto.nome = request.form['nome']
        produto.tamanho = request.form['tamanho']
        produto.categoria = request.form['categoria']
        produto.objeto = request.form['objeto']
        
        # Atualiza Preço de VENDA (campo 'valor_venda' do HTML)
        produto.valor = float(request.form['valor_venda'])
        
        # Se o campo estiver vazio, salva como 0.0
        custo = request.form.get('valor_compra')
        produto.valor_compra = float(custo) if custo else 0.0

        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        
        # Redireciona para a lista de produtos (ou home, como preferir)
        return redirect(url_for('home'))

    return render_template('estoque/editar.html', produto=produto)


#excluir produto
@app.route('/estoque/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)
    
    # Apagar todas as movimentações associadas
    Movimentacao.query.filter_by(produto_id=produto.id).delete()
    
    # Apagar o produto
    db.session.delete(produto)
    db.session.commit()

    flash('Produto e movimentações removidos!', 'success')
    return redirect(url_for('home'))

#-----------------------------------------------
#- entrada e saida estoque

@app.route('/movimentacao', methods=['GET', 'POST'])
@login_required
def movimentacao():
    produtos = Produto.query.all()
    
    # Define para onde voltar
    rota_destino = 'home' if hasattr(current_user, 'role') and current_user.role == 'gerente' else 'funcionario'

    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        tipo = request.form.get('tipo')
        data_str = request.form.get('data')

        # Tenta converter quantidade
        try:
            quantidade = float(request.form.get('quantidade'))
        except (ValueError, TypeError):
            flash("Quantidade inválida!", "error")
            return redirect(url_for(rota_destino))

        # Validações Básicas
        if not produto_id or not tipo or not quantidade:
            flash("Preencha todos os campos!", "error")
            return redirect(url_for(rota_destino))

        produto = Produto.query.get(produto_id)
        if not produto:
            flash("Produto não encontrado!", "error")
            return redirect(url_for(rota_destino))

        if quantidade <= 0:
            flash("A quantidade deve ser maior que zero!", "error")
            return redirect(url_for(rota_destino))

        # --- VALIDAÇÃO DE ESTOQUE (Apenas para SAÍDA) ---
        # Impede que o estoque fique negativo
        if tipo == "saida":
            estoque_atual = produto.calcular_estoque()
            if quantidade > estoque_atual:
                flash(f"Estoque insuficiente! Você tentou tirar {quantidade}, mas só tem {estoque_atual}.", "error")
                return redirect(url_for(rota_destino)) 

        # Converter data
        try:
            data_obj = datetime.strptime(data_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            data_obj = datetime.utcnow()

        # Calcular novo estoque (apenas para registro)
        estoque_atual = produto.calcular_estoque()
        if tipo == "entrada":
            novo_estoque = estoque_atual + quantidade
        elif tipo == "saida":
            novo_estoque = estoque_atual - quantidade
        else:
            flash("Tipo inválido!", "error")
            return redirect(url_for(rota_destino))

        # Criar movimentação
        mov = Movimentacao(
            produto_id=produto_id,
            tipo=tipo,
            quantidade=quantidade,
            data=data_obj,
            estoque_apos_movimentacao=novo_estoque,
            usuario_id=current_user.id if hasattr(current_user, 'id') else None
        )

        db.session.add(mov)
        db.session.commit()
        
        if tipo == 'saida':
    # Usamos 'error' ou 'danger' (se tivesse configurado) para cor vermelha
            flash(f"{tipo.capitalize()} registrada com sucesso! Estoque atualizado para {novo_estoque}", "error") 
        else: # tipo == 'entrada'
            # Usa 'success' para cor verde (como antes)
            flash(f"{tipo.capitalize()} registrada com sucesso!", "success")
        return redirect(url_for(rota_destino))

    # Se for GET
    if hasattr(current_user, 'role') and current_user.role == 'gerente':
        return render_template("home.html", produtos=produtos)
    else:
        return redirect(url_for('funcionario'))



#----------------------------------------------------------
@app.route("/pdf")
def gerar_pdf():
    # Obtenha todos os produtos do banco
    produtos = Produto.query.all()
    
    # --- ADICIONE ESTA LINHA PARA PEGAR O HISTÓRICO ---
    # Pega todas as movimentações ordenadas da mais recente para a mais antiga
    movimentacoes = Movimentacao.query.order_by(Movimentacao.data.desc()).all()    # --------------------------------------------------

    estoque_baixo = [produto for produto in produtos if produto.calcular_estoque() < 20]
    quantidade_produtos_baixo_estoque = len(estoque_baixo)
    
    # Prepare os dados para o template do PDF
    html = render_template(
        "pdf.html", 
        nome_empresa="Impacto Multimarcas",
        produtos=produtos,
        # --- ADICIONE ESTA LINHA PARA ENVIAR AO HTML ---
        movimentacoes=movimentacoes, 
        # -----------------------------------------------
        quantidade_produtos_baixo_estoque=quantidade_produtos_baixo_estoque 
    )

    css_path = os.path.join(os.getcwd(), 'static', 'pdf.css')
    pdf = pdfkit.from_string(html, False)

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=estoque.pdf"

    return response


@app.route('/quantidade_vs_valor')
@login_required
def quantidade_vs_valor():
    # Obter todos os produtos
    produtos = Produto.query.all()

    # Inicializando variáveis para somar
    total_quantidade = 0
    total_valor_compra = 0
    #----
    movimentacoes = Movimentacao.query.order_by(Movimentacao.data.desc()).all()
    # Somando as quantidades e valores de cada produto
    for produto in produtos:
        quantidade_produto = produto.calcular_estoque()  # Quantidade disponível no estoque
        total_quantidade += quantidade_produto
        total_valor_compra += produto.valor_compra * quantidade_produto  # Valor total baseado na quantidade e custo de compra

    # Passando os dados para o template
    return render_template(
        'quantidade_vs_valor.html',  # Crie este template para exibir os dados
        produtos=produtos,
        total_quantidade=total_quantidade,
        movimentacoes=movimentacoes,
        total_valor_compra=total_valor_compra
    )


@app.route('/api/analise-ia')
@login_required
def analise_ia_api():
    # --- 1. TOP 3 VENDAS (Mantido) ---
    top3_vendas = db.session.query(Produto, func.sum(Movimentacao.quantidade).label('total_saidas')) \
        .join(Movimentacao) \
        .filter(Movimentacao.tipo == 'saida') \
        .group_by(Produto.id) \
        .order_by(desc('total_saidas')) \
        .limit(3) \
        .all()

    if top3_vendas:
        lista_html = "<ul class='list-decimal list-inside mt-1 space-y-1'>"
        for item in top3_vendas:
            produto = item[0]
            qtd = int(item[1])
            lista_html += f"<li><strong>{produto.nome}</strong> ({qtd} un.)</li>"
        lista_html += "</ul>"
        mensagem_top = f"Os campeões de vendas são:{lista_html}"
    else:
        mensagem_top = "Ainda não há dados de vendas suficientes."

    # --- 2. TOP 3 PIORES ESTOQUES (Mantido) ---
    produtos = Produto.query.all()
    lista_criticos = []

    for p in produtos:
        atual = p.calcular_estoque()
        if atual <= 10:
            lista_criticos.append({'nome': p.nome, 'qtd': int(atual)})
    
    lista_criticos.sort(key=lambda x: x['qtd'])
    top3_criticos = lista_criticos[:3]

    if top3_criticos:
        lista_html_crit = "<ul class='list-disc list-inside mt-1 space-y-1'>"
        for item in top3_criticos:
            cor = "text-red-700 font-extrabold" if item['qtd'] == 0 else "text-red-700"
            lista_html_crit += f"<li class='{cor}'><strong>{item['nome']}</strong>: Restam {item['qtd']}</li>"
        lista_html_crit += "</ul>"
        mensagem_critico = f"Estes itens precisam de atenção urgente:{lista_html_crit}"
    else:
        mensagem_critico = "Seu estoque está saudável. Nenhum item abaixo de 10 unidades."

    # --- 3. PRODUTOS PARADOS HÁ 30 DIAS (NOVO!) ---
    data_limite = datetime.now() - timedelta(days=30)
    produtos_parados = []

    for p in produtos:
        # Só me importo se tiver estoque (não adianta dar desconto em algo que acabou)
        if p.calcular_estoque() > 0:
            # Busca a ÚLTIMA venda (saída) desse produto
            ultima_venda = Movimentacao.query.filter(
                Movimentacao.produto_id == p.id, 
                Movimentacao.tipo == 'saida'
            ).order_by(Movimentacao.data.desc()).first()

            # Se nunca vendeu OU a última venda é mais velha que 30 dias
            if not ultima_venda or ultima_venda.data < data_limite:
                produtos_parados.append(p.nome)

    # --- DEFININDO A SUGESTÃO FINAL ---
    # Prioridade 1: Se tem produto encalhado, sugere desconto
    if produtos_parados:
        # Pega no máximo 2 nomes para não ficar texto gigante
        nomes = ", ".join(produtos_parados[:5])
        if len(produtos_parados) > 5:
            nomes += " e outros"
        
        sugestao = f"📉 <strong>Liquidação Necessária!</strong> Os itens: <u>{nomes}</u> estão sem saída há mais de 30 dias. Aplique desconto."
    
    # Prioridade 2: Se não tem encalhado, mas tem crítico, sugere reposição
    elif top3_criticos:
        pior_produto = top3_criticos[0]['nome']
        sugestao = f"📦 <strong>Reposição!</strong> Priorize a compra de {pior_produto} para evitar ruptura."
    
    # Prioridade 3: Tudo ok
    else:
        sugestao = "✅ <strong>Tudo Ótimo!</strong> Seu estoque gira bem. Que tal criar combos para aumentar o ticket médio?"

    # --- 4. RETORNO JSON ---
    return jsonify({
        'mensagem_top': mensagem_top,
        'mensagem_critico': mensagem_critico,
        'sugestao': sugestao
    })

@app.route('/criar_usuario', methods=['POST'])
@login_required
def criar_usuario():
    # Segurança: Apenas gerente
    if not hasattr(current_user, 'role') or current_user.role != 'gerente':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('home'))

    nome = request.form.get('username')
    senha = request.form.get('password')
    cpf = request.form.get('cpf')
    cidade = request.form.get('city')
    role = request.form.get('role')
    palavra_seguranca = request.form.get('security_word')

    # Validação básica (SEM EMAIL)
    if not nome or not senha or not cpf:
        flash('Preencha os campos obrigatórios.', 'danger')
        return redirect(url_for('home'))

    # Verifica se usuário já existe
    if Usuario.query.filter_by(nome=nome).first():
        flash('Nome de usuário já existe.', 'danger')
        return redirect(url_for('home'))


    # === VALIDAÇÃO DA SENHA MESTRA (coxinha123) ===
    if role == 'gerente':
        if palavra_seguranca != 'coxinha123':
            flash('ERRO: Palavra de segurança incorreta! Você precisa da senha mestra para criar um Gerente.', 'danger')
            return redirect(url_for('home'))
    # ==============================================

    # --- TRUQUE PARA O BANCO NÃO RECLAMAR ---
    # Como o banco exige email, geramos um falso automático
    email_ficticio = f"{nome.lower().replace(' ', '')}@sistema.local"

    novo = Usuario(
        nome=nome,
        email=email_ficticio, # Salvamos o email gerado
        senha=generate_password_hash(senha),
        cpf=cpf,
        cidade=cidade,
        role=role,
        palavra_seguranca=palavra_seguranca
    )
    
    db.session.add(novo)
    db.session.commit()
    flash(f'Usuário {nome} criado com sucesso!', 'success')
    return redirect(url_for('home'))


# --- ESTA É A ROTA QUE ESTAVA FALTANDO E CAUSOU O ERRO ---
@app.route('/excluir_usuario/<int:id>', methods=['POST'])
@login_required
def excluir_usuario(id):
    if not hasattr(current_user, 'role') or current_user.role != 'gerente':
        flash('Apenas gerentes podem excluir contas.', 'danger')
        return redirect(url_for('home'))
        
    if id == current_user.id:
        flash('Você não pode excluir sua própria conta!', 'danger')
        return redirect(url_for('home'))

    user = Usuario.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuário removido com sucesso.', 'success')
    return redirect(url_for('home'))


@app.route('/trocar_senha', methods=['POST'])
@login_required
def trocar_senha():
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')
    # Captura a palavra de segurança do formulário
    palavra_seguranca = request.form.get('security_word')
    # 1. Verifica se a senha atual está correta
    if not check_password_hash(current_user.senha, senha_atual):
        flash('A senha atual está incorreta.', 'danger')
        return redirect(url_for('home'))

    # 2. Verifica se a nova senha confere com a confirmação
    if nova_senha != confirmar_senha:
        flash('As novas senhas não coincidem.', 'danger')
        return redirect(url_for('home'))

    # 3. Verifica tamanho mínimo (segurança básica)
    if len(nova_senha) < 6:
        flash('A nova senha deve ter no mínimo 6 caracteres.', 'danger')
        return redirect(url_for('home'))

    # 4. Salva a nova senha criptografada
    current_user.senha = generate_password_hash(nova_senha)
    db.session.commit()

    flash('Sua senha foi alterada com sucesso!', 'success')
    return redirect(url_for('home'))


@app.route('/redefinir_senha_publica', methods=['POST'])
def redefinir_senha_publica():
    # 1. Coleta dos dados
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    cidade = request.form.get('cidade')
    palavra_seguranca = request.form.get('palavra_seguranca') # Campo opcional/admin
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')

    # 2. Validação inicial das senhas
    if nova_senha != confirmar_senha:
        flash('As novas senhas não coincidem.', 'error')
        return redirect(url_for('login'))

    # 3. Busca o usuário com base nos dados de verificação
    usuario = Usuario.query.filter_by(
        nome=nome, 
        cpf=cpf, 
        cidade=cidade
    ).first()

    if not usuario:
        flash('Dados de verificação incorretos. Verifique Usuário, CPF e Cidade.', 'error')
        return redirect(url_for('login'))

    # 4. Regra de SEGURANÇA ADICIONAL para GERENTE
    if usuario.role == 'gerente':
        # Verifica se a palavra de segurança foi fornecida e se está correta
        if not palavra_seguranca or palavra_seguranca.lower() != 'coxinha123':
            flash('Você é um Gerente. A palavra de segurança está incorreta.', 'error')
            return redirect(url_for('login'))
        # Nota: Você pode ajustar para checar a palavra do banco, mas o pedido foi 'coxinha123'

    # 5. Se a verificação passou (e passou a regra do Gerente se aplicável), atualiza a senha
    usuario.senha = generate_password_hash(nova_senha)
    db.session.commit()
    
    flash('Sua senha foi redefinida com sucesso! Você pode entrar agora.', 'success')
    return redirect(url_for('login'))



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        # --- CRIA APENAS O GERENTE SE NÃO EXISTIR ---
        gerente = Usuario.query.filter_by(nome='gerente').first()
        if not gerente:
            print("Criando usuário Gerente...")
            novo_gerente = Usuario(
                nome='gerente', 
                email='gerente@impacto.com', 
                senha=generate_password_hash('admin123'), 
                cpf='00000000000',
                role='gerente' # Define como gerente
            )
            db.session.add(novo_gerente)
            db.session.commit()

        # (A parte que criava o funcionário foi removida)

    app.run(debug=True, port=5001)

