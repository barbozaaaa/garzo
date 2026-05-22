"""
Módulo de análise e inteligência do Ateliê Haiti.
Todos os cálculos são feitos em Python puro — sem dependências externas.
"""

from datetime import datetime, timedelta
from collections import defaultdict


# ─── Alertas de Estoque ───────────────────────────────────────────────────────

def alertas_estoque(materiais, movimentacoes):
    """Retorna materiais com estoque abaixo do mínimo, com estimativa de dias restantes."""
    alertas = []
    for m in materiais:
        if m['quantidade_atual'] <= m['quantidade_minima']:
            media = calcular_media_consumo_diario(movimentacoes, m['id'])
            dias_restantes = None
            if media > 0 and m['quantidade_atual'] > 0:
                dias_restantes = int(m['quantidade_atual'] / media)
            alertas.append({
                'material': m,
                'dias_restantes': dias_restantes,
                'media_diaria': round(media, 2),
            })
    return alertas


# ─── Consumo Médio ────────────────────────────────────────────────────────────

def calcular_media_consumo_diario(movimentacoes, material_id, dias=30):
    """Consumo médio diário de um material nos últimos N dias."""
    cutoff = datetime.now() - timedelta(days=dias)
    saidas = [
        m for m in movimentacoes
        if m['material_id'] == material_id
        and m['tipo'] == 'saida'
        and datetime.fromisoformat(m['data']) >= cutoff
    ]
    return sum(s['quantidade'] for s in saidas) / dias


# ─── Item Mais Usado ──────────────────────────────────────────────────────────

def item_mais_usado(movimentacoes, materiais):
    """Retorna o material com maior consumo total."""
    consumo = defaultdict(float)
    for m in movimentacoes:
        if m['tipo'] == 'saida':
            consumo[m['material_id']] += m['quantidade']
    if not consumo:
        return None
    material_id = max(consumo, key=consumo.get)
    material = next((m for m in materiais if m['id'] == material_id), None)
    if not material:
        return None
    return {'material': material, 'total': round(consumo[material_id], 2)}


# ─── Produção Possível ────────────────────────────────────────────────────────

def calcular_producao_possivel(materiais, produtos):
    """
    Para cada produto, calcula quantas unidades podem ser produzidas
    com o estoque atual. Usa a receita (bill of materials) cadastrada.

    Exemplo de retorno:
      [{'produto': {...}, 'quantidade_possivel': 3, 'gargalo': 'Courino Preto'}]
    """
    estoque = {m['id']: m for m in materiais}
    resultado = []

    for produto in produtos:
        receita = produto.get('receita', [])
        if not receita:
            resultado.append({'produto': produto, 'quantidade_possivel': 0, 'gargalo': None})
            continue

        minimo = float('inf')
        gargalo = None

        for ingrediente in receita:
            mat = estoque.get(ingrediente['material_id'])
            necessario = ingrediente['quantidade']
            if not mat or necessario <= 0:
                minimo = 0
                break
            possivel = int(mat['quantidade_atual'] / necessario)
            if possivel < minimo:
                minimo = possivel
                gargalo = mat['nome']

        resultado.append({
            'produto': produto,
            'quantidade_possivel': minimo if minimo != float('inf') else 0,
            'gargalo': gargalo,
        })

    return resultado


# ─── Dados para Gráficos ──────────────────────────────────────────────────────

def consumo_por_categoria(movimentacoes, materiais):
    """Consumo total agrupado por categoria (para gráfico de pizza)."""
    cat_map = {m['id']: m['categoria'] for m in materiais}
    consumo = defaultdict(float)
    for mov in movimentacoes:
        if mov['tipo'] == 'saida':
            cat = cat_map.get(mov['material_id'], 'Outros')
            consumo[cat] += mov['quantidade']
    return dict(sorted(consumo.items(), key=lambda x: x[1], reverse=True))


def consumo_semanal(movimentacoes, semanas=8):
    """Consumo total por semana, nas últimas N semanas (para gráfico de linha)."""
    now = datetime.now()
    labels = []
    totais = []

    for i in range(semanas - 1, -1, -1):
        inicio = now - timedelta(weeks=i + 1)
        fim = now - timedelta(weeks=i)
        label = inicio.strftime('%d/%m')
        total = sum(
            m['quantidade'] for m in movimentacoes
            if m['tipo'] == 'saida'
            and inicio <= datetime.fromisoformat(m['data']) < fim
        )
        labels.append(label)
        totais.append(round(total, 2))

    return {'labels': labels, 'totais': totais}


def top_materiais_consumidos(movimentacoes, materiais, top=5):
    """Top N materiais mais consumidos (para gráfico de barras)."""
    consumo = defaultdict(float)
    for m in movimentacoes:
        if m['tipo'] == 'saida':
            consumo[m['material_id']] += m['quantidade']

    nome_map = {m['id']: m['nome'] for m in materiais}
    ordenado = sorted(consumo.items(), key=lambda x: x[1], reverse=True)[:top]

    return {
        'labels': [nome_map.get(mid, 'Desconhecido') for mid, _ in ordenado],
        'totais': [round(v, 2) for _, v in ordenado],
    }
