# 🤖 Automação de Extração de Comissões - SulAmérica

Este projeto realiza automaticamente a extração de extratos de comissões do portal da SulAmérica e exporta os dados para um arquivo Excel.

---

## ✅ Funcionalidades

- Login automático no portal do corretor
- Seleção das campanhas:
  - CIA SAÚDE (9512)
  - SUASEG (6220)
  - ODONTOLÓGICO SA (9598)
  - SASEG (1309)
- Processa todas as datas disponíveis do mês atual automaticamente
- Extração de informações completas dos clientes
- Classificação do tipo de remuneração:
  - `100%` → Agenciamento
  - `2%` → Vitalício
  - Outros → Outro
- Geração de planilha `extrato_sulamerica.xlsx`
- Execução automática todos os dias às 21h via Docker + cron

---

## 📦 Requisitos

- Python 3.10+
- Google Chrome e ChromeDriver compatível
- Docker (caso vá executar em contêiner)
- Conta ativa no portal SulAmérica Corretor

---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com:

```env
SULA_EMAIL=seu_email_de_login
SULA_SENHA=sua_senha_de_login
