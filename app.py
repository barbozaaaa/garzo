import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import analytics

app = Flask(__name__)
app.secret_key = 'atelie-haiti-2026'

_IS_VERCEL  = os.environ.get('VERCEL')
DATA_DIR    = '/tmp/data'    if _IS_VERCEL else os.path.join(os.path.dirname(__file__), 'data')
UPLOAD_DIR  = '/tmp/uploads' if _IS_VERCEL else os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

os.makedirs(DATA_DIR,   exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─── Helpers JSON ─────────────────────────────────────────────────────────────

def load(filename, default=None):
    if default is None:
        default = []
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default


def save(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def salvar_foto(file_obj):
    if not file_obj or not file_obj.filename or not allowed(file_obj.filename):
        return None
    ext = file_obj.filename.rsplit('.', 1)[1].lower()
    nome = f"{uuid.uuid4()}.{ext}"
    file_obj.save(os.path.join(UPLOAD_DIR, nome))
    return nome


def registrar_movimentacao(material_id, tipo, quantidade, motivo=''):
    movs = load('movimentacoes.json')
    movs.append({
        'id':          str(uuid.uuid4()),
        'material_id': material_id,
        'tipo':        tipo,
        'quantidade':  quantidade,
        'data':        datetime.now().isoformat(),
        'motivo':      motivo,
    })
    save('movimentacoes.json', movs)


# ─── Seed de dados (executa apenas na primeira vez) ───────────────────────────

def seed_inicial():
    if load('materiais.json'):
        return
    ids = [str(uuid.uuid4()) for _ in range(6)]
    materiais = [
        {'id': ids[0], 'nome': 'Courino Preto',          'categoria': 'Courino',   'quantidade_atual': 8.5, 'quantidade_minima': 3.0, 'unidade': 'metros',   'custo_unitario': 45.0, 'foto': None, 'criado_em': datetime.now().isoformat()},
        {'id': ids[1], 'nome': 'Mosquetão Dourado',       'categoria': 'Metal',     'quantidade_atual': 4,   'quantidade_minima': 10,  'unidade': 'unidades', 'custo_unitario': 3.5,  'foto': None, 'criado_em': datetime.now().isoformat()},
        {'id': ids[2], 'nome': 'Zíper 30cm Preto',        'categoria': 'Aviamento', 'quantidade_atual': 12,  'quantidade_minima': 5,   'unidade': 'unidades', 'custo_unitario': 4.0,  'foto': None, 'criado_em': datetime.now().isoformat()},
        {'id': ids[3], 'nome': 'Linha de Costura Preta',  'categoria': 'Aviamento', 'quantidade_atual': 2,   'quantidade_minima': 3,   'unidade': 'rolos',    'custo_unitario': 8.0,  'foto': None, 'criado_em': datetime.now().isoformat()},
        {'id': ids[4], 'nome': 'Courino Caramelo',        'categoria': 'Courino',   'quantidade_atual': 3.0, 'quantidade_minima': 2.0, 'unidade': 'metros',   'custo_unitario': 45.0, 'foto': None, 'criado_em': datetime.now().isoformat()},
        {'id': ids[5], 'nome': 'Fivela Quadrada Dourada', 'categoria': 'Metal',     'quantidade_atual': 8,   'quantidade_minima': 5,   'unidade': 'unidades', 'custo_unitario': 5.0,  'foto': None, 'criado_em': datetime.now().isoformat()},
    ]
    save('materiais.json', materiais)

    # Produto de exemplo com receita
    bolsa_id = str(uuid.uuid4())
    save('produtos.json', [{
        'id':         bolsa_id,
        'nome':       'Bolsa Tote Clássica',
        'foto':       None,
        'preco_venda': 150.0,
        'receita': [
            {'material_id': ids[0], 'quantidade': 0.5},
            {'material_id': ids[1], 'quantidade': 2},
            {'material_id': ids[2], 'quantidade': 1},
        ],
        'criado_em': datetime.now().isoformat(),
    }])

    # Algumas movimentações de exemplo para os gráficos
    for mid, qtd in [(ids[0], 0.5), (ids[1], 2), (ids[2], 1), (ids[0], 1.0), (ids[3], 1)]:
        registrar_movimentacao(mid, 'saida', qtd, 'Produção de bolsa')


# ─── Rotas ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    materiais    = load('materiais.json')
    movimentacoes = load('movimentacoes.json')
    n_alertas    = len(analytics.alertas_estoque(materiais, movimentacoes))
    return render_template('home.html', n_alertas=n_alertas)


# --- Estoque ------------------------------------------------------------------

@app.route('/estoque')
def estoque():
    todos       = load('materiais.json')
    categoria   = request.args.get('cat', 'Todos')
    busca       = request.args.get('q', '').lower()
    categorias  = sorted(set(m['categoria'] for m in todos))
    filtrados   = [
        m for m in todos
        if (categoria == 'Todos' or m['categoria'] == categoria)
        and busca in m['nome'].lower()
    ]
    return render_template('estoque.html',
        materiais=filtrados, categorias=categorias,
        categoria_ativa=categoria, busca=busca)


@app.route('/estoque/<mid>/entrada', methods=['POST'])
def entrada(mid):
    materiais = load('materiais.json')
    qtd = float(request.form.get('quantidade', 0))
    motivo = request.form.get('motivo', 'Compra')
    for m in materiais:
        if m['id'] == mid:
            m['quantidade_atual'] += qtd
            flash(f'✅ +{qtd} {m["unidade"]} de "{m["nome"]}" adicionados!')
            break
    save('materiais.json', materiais)
    registrar_movimentacao(mid, 'entrada', qtd, motivo)
    return redirect(url_for('estoque'))


@app.route('/estoque/<mid>/excluir', methods=['POST'])
def excluir_material(mid):
    materiais = [m for m in load('materiais.json') if m['id'] != mid]
    save('materiais.json', materiais)
    flash('🗑️ Material removido.')
    return redirect(url_for('estoque'))


# --- Adicionar Material -------------------------------------------------------

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        materiais = load('materiais.json')
        foto = salvar_foto(request.files.get('foto'))
        novo = {
            'id':               str(uuid.uuid4()),
            'nome':             request.form['nome'].strip(),
            'categoria':        request.form['categoria'],
            'quantidade_atual': float(request.form.get('quantidade', 0)),
            'quantidade_minima': float(request.form.get('quantidade_minima', 5)),
            'unidade':          request.form.get('unidade', 'unidades'),
            'custo_unitario':   float(request.form.get('custo', 0)),
            'foto':             foto,
            'criado_em':        datetime.now().isoformat(),
        }
        materiais.append(novo)
        save('materiais.json', materiais)
        registrar_movimentacao(novo['id'], 'entrada', novo['quantidade_atual'], 'Estoque inicial')
        flash(f'✅ "{novo["nome"]}" adicionado ao estoque!')
        return redirect(url_for('estoque'))
    return render_template('adicionar.html')


# --- Dar Baixa ---------------------------------------------------------------

@app.route('/baixa', methods=['GET', 'POST'])
def baixa():
    materiais = load('materiais.json')
    if request.method == 'POST':
        mid  = request.form['material_id']
        qtd  = float(request.form['quantidade'])
        for m in materiais:
            if m['id'] == mid:
                if qtd > m['quantidade_atual']:
                    flash(f'⚠️ Tem só {m["quantidade_atual"]} {m["unidade"]} de "{m["nome"]}"!')
                    return redirect(url_for('baixa'))
                m['quantidade_atual'] = round(m['quantidade_atual'] - qtd, 4)
                flash(f'✅ Baixa de {qtd} {m["unidade"]} de "{m["nome"]}" registrada!')
                break
        save('materiais.json', materiais)
        registrar_movimentacao(mid, 'saida', qtd, request.form.get('motivo', 'Uso em produção'))
        return redirect(url_for('estoque'))
    return render_template('baixa.html', materiais=materiais)


# --- Produtos e Receitas ------------------------------------------------------

@app.route('/produtos')
def produtos():
    materiais = load('materiais.json')
    prods     = load('produtos.json')
    producao  = analytics.calcular_producao_possivel(materiais, prods)
    # Enriquece a receita com nome e unidade de cada material
    mat_map = {m['id']: m for m in materiais}
    for item in producao:
        for ing in item['produto'].get('receita', []):
            mat = mat_map.get(ing['material_id'], {})
            ing['nome']    = mat.get('nome', '—')
            ing['unidade'] = mat.get('unidade', '')
    return render_template('produtos.html', producao=producao)


@app.route('/produtos/novo', methods=['GET', 'POST'])
def novo_produto():
    materiais = load('materiais.json')
    if request.method == 'POST':
        prods = load('produtos.json')
        foto  = salvar_foto(request.files.get('foto'))
        ids   = request.form.getlist('mat_id[]')
        qtds  = request.form.getlist('mat_qtd[]')
        receita = [
            {'material_id': mid, 'quantidade': float(qtd)}
            for mid, qtd in zip(ids, qtds) if mid and qtd
        ]
        prods.append({
            'id':          str(uuid.uuid4()),
            'nome':        request.form['nome'].strip(),
            'foto':        foto,
            'preco_venda': float(request.form.get('preco_venda', 0)),
            'receita':     receita,
            'criado_em':   datetime.now().isoformat(),
        })
        save('produtos.json', prods)
        flash(f'✅ Produto cadastrado!')
        return redirect(url_for('produtos'))
    return render_template('novo_produto.html', materiais=materiais)


@app.route('/produtos/<pid>/excluir', methods=['POST'])
def excluir_produto(pid):
    save('produtos.json', [p for p in load('produtos.json') if p['id'] != pid])
    flash('🗑️ Produto removido.')
    return redirect(url_for('produtos'))


# --- Alertas e BI ------------------------------------------------------------

@app.route('/alertas')
def alertas():
    materiais     = load('materiais.json')
    movs          = load('movimentacoes.json')
    prods         = load('produtos.json')

    alertas_list  = analytics.alertas_estoque(materiais, movs)
    mais_usado    = analytics.item_mais_usado(movs, materiais)
    producao      = analytics.calcular_producao_possivel(materiais, prods)
    consumo_cat   = analytics.consumo_por_categoria(movs, materiais)
    semanal       = analytics.consumo_semanal(movs)
    top_mat       = analytics.top_materiais_consumidos(movs, materiais)

    return render_template('alertas.html',
        alertas=alertas_list,
        mais_usado=mais_usado,
        producao=producao,
        consumo_cat=json.dumps(consumo_cat, ensure_ascii=False),
        semanal=json.dumps(semanal, ensure_ascii=False),
        top_mat=json.dumps(top_mat, ensure_ascii=False),
    )


# ─── Start ────────────────────────────────────────────────────────────────────

seed_inicial()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
