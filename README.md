# Trabalho-1-Comp.-Graf.

# ✅ To-Do mínimo (Python + PySide6)

## Must-have (entrega)
- [ ] **App base**: janela + `Canvas` (QWidget) e `QPainter` no `paintEvent`.
- [ ] **Clique → vértice**: adicionar ponto e desenhar aresta em tempo real (linha fantasma).
- [ ] **Fechar polígono** (botão/Enter) com validação (≥3 vértices, não degenerado).
- [ ] **ET (Edge Table)**: construir a partir dos vértices (ignorar horizontais, tratar topo/fundo).
- [ ] **AET (Active Edge Table)**: atualização por *scanline*, `x += 1/m` incremental.
- [ ] **Paridade even-odd**: ordenar interseções e preencher spans `[x1,x2), [x3,x4)…`.
- [ ] **Desenho do fill**: pintar spans por `drawLine`/`fillRect` (1 pixel por *scanline*).
- [ ] **Contorno**: desenhar borda com **cor** e **espessura** configuráveis.
- [ ] **Ações básicas**: **Desfazer último vértice**, **Limpar**, **Preencher**.
- [ ] **Salvar/Abrir polígono** em JSON (lista de vértices + estilos).
- [ ] **Screenshots** do canvas (PNG) para o relatório.
- [ ] **Casos de teste visuais**: triângulo, retângulo, polígono côncavo, estrela (auto-interseção).

## Nice-to-have (se der tempo)
- [ ] **Modo winding** (non-zero) além do even-odd (checkbox).
- [ ] **Antialiasing** opcional; *double buffering* se necessário.
- [ ] **Snap** opcional a grade; clamping ao viewport.
- [ ] **Medições** simples: tempo de build da ET/AET e do preenchimento.

## Arquivos sugeridos (curto)
- `src/app.py` — inicia a janela.
- `src/ui/canvas.py` — eventos de mouse + pintura.
- `src/core/scanline.py` — ET/AET + preenchimento.
- `src/core/polygon.py` — estrutura dos vértices e utilidades.
- `src/io/serde.py` — salvar/abrir JSON.

## Como Executar

1.  **Abra um terminal** (CMD, PowerShell ou outro de sua preferência).

2.  **Navegue até a pasta do seu projeto**, onde o arquivo `setup.py` está localizado.
    ```bash
    cd caminho\para\seu\projeto
    ```

3.  **Execute o comando** para iniciar o processo de compilação:
    ```bash
    python setup.py py2exe
    ```

Ao final do processo, uma nova pasta chamada **`dist`** será criada no seu diretório. Dentro dela, você encontrará o arquivo **`app.exe`** junto com todos os outros arquivos e DLLs necessários.

> **Importante**: Para que o programa funcione em outro computador, você precisa copiar e distribuir a pasta **`dist`** inteira.
