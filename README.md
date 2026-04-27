# libteca

Aplicação web de gestão de biblioteca escolar. Permite pesquisar e requisitar livros do Plano Nacional de Leitura (PNL) e gerir o ciclo de vida dos empréstimos do lado administrativo.

- Produção: https://libteca.onrender.com
- Repositório: https://github.com/pedrojocmota/libteca

---

## Requisitos

- Python 3.10+
- pip

---

## Correr localmente

**1. Clonar o repositório**

```bash
git clone https://github.com/pedrojocmota/libteca.git
cd libteca
```

**2. Criar e ativar o ambiente virtual**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Instalar dependências**

```bash
pip install -r requirements.txt
```

**4. Aplicar migrações**

```bash
python manage.py migrate
```

**5. Carregar os livros**

```bash
python manage.py loaddata library/fixtures/books.json
```

**6. Iniciar o servidor**

```bash
python manage.py runserver
```

Aceder em: http://127.0.0.1:8000

---

## Endpoints

| Endpoint | Método | Descrição |
|---|---|---|
| /login | GET / POST | Autenticação |
| /register | GET / POST | Registo de utilizador |
| /logout | GET | Terminar sessão |
| /catalog | GET | Catálogo de livros |
| /borrow/\<id\> | GET / POST | Pedido de empréstimo |
| /my-books | GET | Livros do utilizador |
| /admin-panel | GET | Painel de administração |
| /admin-panel/\<id\>/\<action\> | GET | Aprovar / rejeitar / devolver |
| /admin | GET | Django Admin |

---
