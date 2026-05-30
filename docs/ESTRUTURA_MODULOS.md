# Estrutura dos Módulos — Casa 3D

## O que é MOD-001?

Identificador de um **módulo construtivo** da casa demo.

- Formato: `MOD-NNN` (001 a 015)
- Definido na planilha e no HTML 3D

```
Planilha                    HTML 3D
┌─────────────┐            ┌──────────────┐
│ MOD-001     │ ────────►  │ mesh fundação│
│ Fundação    │            │ userData.id  │
│ CONCLUIDO   │            └──────────────┘
└─────────────┘
```

## Status e cor

```
Status planilha → status_canonico() → hex → setModuloColor()
```

| Status | Cor |
|--------|-----|
| NAO INICIADO | #B4B4B4 |
| PENDENTE | #FFFFFF |
| EM ANDAMENTO | #5DADE2 |
| CONCLUIDO | #2A9D8F |
| BLOQUEADO | #505050 |
| INSPECIONAR | #E74C3C |

## Módulos vizinhos

Usa **LINHA_MAPA** e **COLUNA_MAPA** da planilha:

```
Para MOD-009 (linha 2, coluna 2):
  linha ∈ [1, 3]
  coluna ∈ [0, 4]   (coluna-2 .. coluna+2)
```

## Perímetro

Intervalo numérico: MOD-001 até MOD-005 (não confundir com vizinhança no mapa).

## Diagrama da casa

```
        [MOD-007 telhado E]  [MOD-008 telhado D]
    ┌─────────────────────────────────────────┐
    │ MOD-005    MOD-003 frente    MOD-006    │
    │ lateral    MOD-009 porta     lateral  │
    │ esq        MOD-010 janela      dir     │
    │            MOD-004 traseira             │
    ├─────────────────────────────────────────┤
    │ MOD-002 piso                            │
    │ MOD-001 fundação                        │
    └─────────────────────────────────────────┘
     MOD-014 varanda    MOD-015 jardim   MOD-012 garagem
                        MOD-013 chaminé
```

Legenda completa: `saida_casa_3d/legenda_status.json`
