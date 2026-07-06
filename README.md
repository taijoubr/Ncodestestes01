# Oloroke Birigui - Site Oficial

Site institucional oficial do **Oloroke Birigui**, desenvolvido com foco em paz, espiritualidade, elegância e alta performance.

O projeto foi construído utilizando **Python 3**, **FastAPI**, **Jinja2** e **SQLAlchemy**, com uma arquitetura preparada para integração direta com bancos de dados relacionais (PostgreSQL/Supabase) e expansão para um sistema administrativo robusto.

---

## 🎨 Design e Identidade Visual

O design foi planejado para transmitir paz e reverência, utilizando uma paleta sóbria e elegante:
- **Cor Principal:** Azul Escuro (`#0B1F3A`) - representando o manto protetor espiritual e serenidade.
- **Cor Secundária:** Branco (`#FFFFFF`) - representando a paz, pureza e a vibração de Oxalá.
- **Cor Complementar:** Cinza Claro (`#F5F7FA`) - para suavidade e contraste confortável.
- **Detalhes:** Azul Médio (`#1E4D8C`) - simbolizando a força das águas e dos caminhos.

O site foi estruturado sem frameworks CSS pesados (como Bootstrap ou Tailwind), utilizando **CSS Puro (Grid e Flexbox)**, garantindo carregamento ultrarrápido e código limpo.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.10+ (FastAPI, Uvicorn)
- **Engine de Templates:** Jinja2 (HTML5 semântico com herança de blocos)
- **Estilização:** CSS3 puro e responsivo (Mobile-first para visualização perfeita em celulares, tablets e computadores)
- **Banco de Dados & ORM:** SQLAlchemy preparado para PostgreSQL (Supabase)
- **SEO & Otimização:** Meta tags completas, Open Graph, Favicon vetorial inline e arquivo `robots.txt`

---

## 📂 Estrutura do Projeto

```text
.
├── app/
│   ├── config.py          # Configurações do ambiente (Database URL, Secrets)
│   ├── database.py        # Configurações de conexão SQLAlchemy & Sessão
│   ├── models.py          # Modelos de dados (User, AgendaEvent, Aviso)
│   ├── routes.py          # Rotas e controladores FastAPI
│   └── main.py            # Ponto de entrada do app (FastAPI App & Startup)
├── templates/
│   ├── base.html          # Template base com Cabeçalho, Menu Responsivo e Rodapé
│   ├── index.html         # Página Inicial (Hero banner, Pilares, Trabalhos, Mural)
│   ├── sobre.html         # Nossa Casa (História, Patronos e Guia de Primeira Vez)
│   ├── agenda.html        # Tabela e Lista Responsiva de Giras/Estudos
│   └── contato.html       # Formulário de Contato e Informações de Localização
├── static/
│   ├── css/
│   │   └── style.css      # Estilização completa e responsiva do site
│   └── robots.txt         # Arquivo de instruções para motores de busca (SEO)
├── requirements.txt       # Dependências de pacotes do Python
├── package.json           # Configuração de scripts para o supervisor do container
└── README.md              # Documentação do projeto (este arquivo)
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
Certifique-se de ter o **Python 3** instalado em sua máquina.

### Execução Local

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o servidor de desenvolvimento:
   ```bash
   python -m uvicorn app.main:app --port 3000 --reload
   ```

3. Abra o navegador em: [http://localhost:3000](http://localhost:3000)

---

## 🔮 Preparado para Expansão

A arquitetura do projeto foi estruturada de forma modular, permitindo a fácil acoplagem de novas funcionalidades sem a necessidade de reescrever o código existente:

1. **Painel Administrativo:** Os modelos de banco de dados (`User`) e rotas já estão estruturados para receber futuramente autenticação JWT ou baseada em sessão.
2. **Cadastro de Médiuns e Consulentes:** Relações podem ser adicionadas estendendo o `models.py`.
3. **Mural e Agenda Dinâmicos:** As rotas do site já estão configuradas para fazer queries reais no banco de dados, utilizando os exemplos estáticos como um fallback seguro caso a conexão não esteja ativa, de modo que o site nunca fique "quebrado" ou vazio.
4. **API para Aplicativo Mobile:** As rotas podem ser facilmente estendidas ou novos endpoints `@app.get("/api/v1/...")` podem ser declarados retornando JSON diretamente, aproveitando a mesma lógica e banco de dados do site oficial.
