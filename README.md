# Wall Display

![Language](https://img.shields.io/github/languages/top/agslima/wall-display?style=flat-square)
![License](https://img.shields.io/github/license/agslima/wall-display?style=flat-square)

Projeto simples em **Python** criado para exibir imagens (ou conteúdos visuais) em um monitor, com transições suaves, ideal para rodar em dispositivos embarcados como **Raspberry Pi**.

> Ideal para exibir slides, quadros informativos, galerias ou conteúdo visual contínuo em instalações físicas.

---

## Funcionalidades

- Interface fullscreen automática (usando `pygame`)
- Transição com **fade in/fade out** entre imagens
- Leitura dinâmica de diretórios a partir de um arquivo `menu.data`
- Timer de apresentação automática e controle manual por teclado
- Suporte nativo a `.jpg`

---

## Estrutura esperada

O programa espera uma pasta chamada `menu-data/` com um arquivo `menu.data` no seguinte formato:

```csv
1:imagens/eventos:1:Eventos:Imagens dos últimos eventos
2:imagens/avisos:1:Avisos:Comunicados importantes
