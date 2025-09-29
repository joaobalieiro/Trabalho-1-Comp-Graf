from __future__ import annotations
from typing import Dict, List, Tuple
from PySide6.QtCore import QPointF
import math

Span = Tuple[int, int]
SpansByY = Dict[int, List[Span]]

def scanline_fill_even_odd(vertices: List[QPointF]) -> SpansByY:
    """
    Preenchimento por scanline usando ET / AET.
    Retorna dicionário { y_int : [(x1,x2), (x3,x4), ...] } com spans por linha (intervalos inteiros inclusivos).
    Observações:
      - Usa scanline "center" em y + 0.5 para evitar duplicidade em vértices.
      - Remove arestas horizontais.
      - vertices podem estar em qualquer ordem (fecha o polígono implicitamente).
    """
    if len(vertices) < 3:
        return {}

    # Helper para acessar float das QPointF
    def xf(p: QPointF) -> float:
        return float(p.x())
    def yf(p: QPointF) -> float:
        return float(p.y())

    # Fecha polígono se necessário
    verts = vertices[:] if vertices[0] != vertices[-1] else vertices[:]
    if verts[0] != verts[-1]:
        verts.append(verts[0])

    # Construir Edge Table (ET): dict[y_start] -> list de edges
    # cada edge será um dict: { 'y_end': int, 'x': float, 'inv_slope': float }
    ET: Dict[int, List[dict]] = {}

    min_y = math.inf
    max_y = -math.inf

    n = len(verts) - 1
    for i in range(n):
        p0 = verts[i]
        p1 = verts[i+1]
        x0, y0 = xf(p0), yf(p0)
        x1, y1 = xf(p1), yf(p1)

        # Ignorar arestas horizontais
        if abs(y1 - y0) < 1e-12:
            continue

        # y menor e maior da aresta
        y_min = min(y0, y1)
        y_max = max(y0, y1)

        # scanline indices (inteiros y) para os quais esta aresta deve estar ativa,
        # usando a convenção de testar a posição y_scan = y + 0.5:
        # queremos y tais que y + 0.5 >= y_min  e  y + 0.5 < y_max
        y_start = math.ceil(y_min - 0.5)
        y_end = math.floor(y_max - 0.5)  # inclusive

        if y_start > y_end:
            # aresta muito pequena para afetar qualquer scanline com essa convenção
            continue

        # inv_slope = dx/dy (incremento de x por incremento de y=1 scanline)
        inv_slope = (x1 - x0) / (y1 - y0)

        # x inicial na scanline y_start: x = x0 + (y_scan - y0) * dx/dy
        y_scan = y_start + 0.5
        x_init = x0 + (y_scan - y0) * inv_slope

        edge_rec = {'y_end': y_end, 'x': x_init, 'inv_slope': inv_slope}
        ET.setdefault(y_start, []).append(edge_rec)

        min_y = min(min_y, y_start)
        max_y = max(max_y, y_end)

    if min_y is math.inf:
        return {}  # sem arestas válidas

    # Varredura: de min_y até max_y inclusive
    AET: List[dict] = []
    spans_by_y: SpansByY = {}

    for y in range(int(min_y), int(max_y) + 1):
        # 1) Inserir arestas da ET para esta scanline
        edges_to_add = ET.get(y, [])
        if edges_to_add:
            AET.extend(edges_to_add)

        # 2) Remover arestas cuja y_end < y (já não estão ativas nesta scanline)
        AET = [e for e in AET if e['y_end'] >= y]

        # 3) Ordenar AET por x atual
        AET.sort(key=lambda e: e['x'])

        # 4) Formar pares (even-odd) e gerar spans
        xs = [e['x'] for e in AET]
        spans: List[Span] = []
        for i in range(0, len(xs), 2):
            if i+1 >= len(xs):
                break  # aresta não pareada (polígono degenerado?) -> ignora
            xL = xs[i]
            xR = xs[i+1]
            # converter para intervalos de pixels inteiros (inclusivos).
            # escolhi ceil(xL) .. floor(xR) — isso preenche pixels cujos centros estão dentro do intervalo
            ixL = math.ceil(xL)
            ixR = math.floor(xR)
            if ixL <= ixR:
                spans.append((ixL, ixR))

        if spans:
            spans_by_y[y] = spans

        # 5) Atualizar x nas arestas ativas para o próximo scanline (y+1)
        for e in AET:
            e['x'] += e['inv_slope']

    return spans_by_y
