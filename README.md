# API de Estoque

API para controle de estoque da loja de variedades, desenvolvida para o desafio técnico de Back-End do Prosel 2026.2 da Ecomp Jr.

A API cadastra categorias, fornecedores e produtos, registra entradas e saídas de estoque com histórico imutável e oferece consultas para identificar produtos com estoque baixo e filtrar o histórico por período ou fornecedor.

## Tecnologias

- Python 3.14
- FastAPI
- PostgreSQL
- SQLAlchemy 2 (ORM)
- Alembic (migrations)
- PyJWT (autenticação)
- Pytest e GitHub Actions (testes e integração contínua)

## Como rodar

Pré-requisitos: Python 3.12 ou mais recente e um PostgreSQL rodando.

1. Clone o repositório e entre na pasta:

```bash
git clone git@github.com:JaiDeveloperpy/desafio_ecompjr.git
cd desafio_ecompjr
```

2. Crie o ambiente virtual e instale as dependências:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Crie o banco no PostgreSQL:

```sql
CREATE DATABASE desafio_ecompjr;
```

4. Copie o arquivo de exemplo e preencha com os seus dados:

```bash
cp .env.example .env
```

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | Endereço do banco, no formato `postgresql+psycopg2://usuario:senha@localhost:5432/desafio_ecompjr` |
| `JWT_SECRET` | Chave usada para assinar os tokens. Use um valor longo e aleatório, por exemplo a saída de `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `JWT_EXPIRA_MINUTOS` | Validade do token em minutos. Padrão: 60 |

5. Crie as tabelas:

```bash
alembic upgrade head
```

6. Crie o primeiro administrador (cadastrar usuários pela API exige um admin logado, então o primeiro precisa ser criado pelo terminal):

```bash
python -m app.criar_admin "Seu Nome" admin@loja.com sua-senha
```

7. Suba a API:

```bash
uvicorn app.main:app --reload
```

A documentação interativa (Swagger) fica em `http://localhost:8000/docs`.

## Autenticação

Todas as rotas, exceto `/health` e `/auth/login`, exigem um token JWT no cabeçalho:

```
Authorization: Bearer <token>
```

Existem dois papéis:

| Papel | Pode fazer |
|---|---|
| `admin` | Tudo: gerenciar categorias, fornecedores, produtos e usuários, além de registrar movimentações |
| `funcionario` | Consultar qualquer dado e registrar movimentações (entradas e saídas) |

No Swagger, faça login em `POST /auth/login`, copie o `access_token`, clique em **Authorize** e cole o token.

## Regras de negócio

- **O estoque só muda por movimentação.** Todo produto começa com `quantidade_em_estoque` igual a 0, e esse campo não pode ser enviado na criação nem na edição. Assim, qualquer alteração no estoque fica registrada no histórico.
- **Movimentações são imutáveis.** Só existem rotas para criar e consultar. Tentativas de editar ou excluir recebem `405` com a mensagem "Método não permitido para esta rota."
- **Saída maior que o estoque é recusada** com `400`, e nada é gravado.
- **Exclusões que quebrariam vínculos são bloqueadas** com `409`: categoria ou fornecedor com produtos vinculados, e produto com movimentações registradas. A opção por bloquear em vez de apagar em cascata evita perder produtos e histórico de auditoria por engano. O banco também garante isso com chaves estrangeiras `ON DELETE RESTRICT`.
- **Campos únicos:** nome da categoria, CNPJ e email do fornecedor, SKU do produto e email do usuário. Duplicidade retorna `409`.
- **CNPJ** é enviado só com os 14 dígitos, sem pontuação, para que o mesmo número não seja cadastrado duas vezes com formatações diferentes.

## Concorrência

Quando dois vendedores registram a saída do mesmo produto ao mesmo tempo, as duas requisições poderiam ler o mesmo estoque e as duas aprovarem a venda, deixando o estoque negativo ou com um valor errado.

Para evitar isso, o registro de movimentação usa **lock pessimista** (`SELECT ... FOR UPDATE`, em `app/services/movimentacao.py`). A linha do produto fica travada do momento em que é lida até o commit. A segunda requisição espera a primeira terminar e só então lê o estoque, já atualizado.

A movimentação e a nova quantidade do produto são gravadas no mesmo commit, então ou as duas coisas acontecem, ou nenhuma.

Como garantia extra, a tabela `produtos` tem uma `CHECK constraint` que impede `quantidade_em_estoque` negativa direto no banco.

O teste `test_saidas_simultaneas_nao_deixam_estoque_negativo` dispara 30 saídas simultâneas de 1 unidade sobre um estoque de 20 e confere que exatamente 20 são aceitas e o estoque termina em 0.

## Formato dos erros

Todos os erros seguem o mesmo formato:

```json
{
  "status": 404,
  "mensagem": "Produto 42 não encontrado."
}
```

Em erros de validação, o campo `detalhes` indica o que está errado:

```json
{
  "status": 400,
  "mensagem": "Dados inválidos.",
  "detalhes": [
    { "campo": "cnpj", "erro": "Formato inválido." },
    { "campo": "email", "erro": "Campo obrigatório." }
  ]
}
```

| Código | Quando acontece |
|---|---|
| 400 | Dados inválidos ou regra de negócio violada (ex.: estoque insuficiente) |
| 401 | Token ausente, inválido ou expirado, ou login incorreto |
| 403 | Usuário sem permissão para a ação |
| 404 | Recurso não encontrado |
| 405 | Método não permitido (ex.: editar movimentação) |
| 409 | Duplicidade ou exclusão bloqueada por vínculo |
| 500 | Erro interno. O detalhe vai apenas para o log do servidor, nunca para a resposta |

## Rotas

Nas tabelas abaixo, "Acesso" indica quem pode usar a rota. Rotas marcadas com "logado" aceitam qualquer usuário autenticado. Todas as rotas protegidas podem retornar `401`, e as de admin também `403`, por isso esses códigos não são repetidos em cada uma.

### Autenticação

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/auth/login` | público | Faz login e devolve o token |
| GET | `/auth/me` | logado | Mostra o usuário dono do token |
| POST | `/usuarios` | admin | Cadastra um usuário |

**POST /auth/login**

```json
{ "email": "admin@loja.com", "senha": "sua-senha" }
```

Resposta `200`:

```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }
```

Erros: `400` (corpo inválido), `401` (email ou senha incorretos).

**POST /usuarios**

```json
{
  "nome": "Maria Souza",
  "email": "maria@loja.com",
  "senha": "senha-forte-123",
  "papel": "funcionario"
}
```

`papel` aceita `admin` ou `funcionario` (padrão). A senha precisa ter pelo menos 8 caracteres.

Resposta `201`:

```json
{ "id": 2, "nome": "Maria Souza", "email": "maria@loja.com", "papel": "funcionario" }
```

Erros: `400`, `409` (email já cadastrado).

### Categorias

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/categorias` | logado | Lista todas |
| GET | `/categorias/{id}` | logado | Busca por id |
| POST | `/categorias` | admin | Cria |
| PATCH | `/categorias/{id}` | admin | Altera |
| DELETE | `/categorias/{id}` | admin | Exclui, se não houver produtos vinculados |

**POST /categorias**

```json
{ "nome": "Decoração" }
```

Resposta `201`:

```json
{ "id": 1, "nome": "Decoração" }
```

Erros: `400` (nome vazio ou com mais de 80 caracteres), `409` (nome já existe).

**PATCH /categorias/{id}** recebe o mesmo corpo, e todos os campos são opcionais. Resposta `200` com a categoria atualizada. Erros: `400`, `404`, `409`.

**DELETE /categorias/{id}** responde `204` sem corpo. Erros: `404`, `409` (categoria com produtos).

### Fornecedores

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/fornecedores` | logado | Lista todos |
| GET | `/fornecedores/{id}` | logado | Busca por id |
| POST | `/fornecedores` | admin | Cria |
| PATCH | `/fornecedores/{id}` | admin | Altera |
| DELETE | `/fornecedores/{id}` | admin | Exclui, se não houver produtos vinculados |

**POST /fornecedores**

```json
{
  "nome": "Importadora Oriente",
  "cnpj": "12345678000190",
  "telefone": "75999990000",
  "email": "contato@oriente.com"
}
```

Resposta `201`:

```json
{
  "id": 1,
  "nome": "Importadora Oriente",
  "cnpj": "12345678000190",
  "telefone": "75999990000",
  "email": "contato@oriente.com"
}
```

Erros: `400` (CNPJ fora do formato de 14 dígitos, email inválido, telefone com menos de 8 caracteres), `409` (CNPJ ou email já cadastrado).

**PATCH /fornecedores/{id}** aceita qualquer subconjunto dos campos acima. Resposta `200`. Erros: `400`, `404`, `409`.

**DELETE /fornecedores/{id}** responde `204`. Erros: `404`, `409` (fornecedor com produtos).

### Produtos

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/produtos` | logado | Lista, com filtros opcionais |
| GET | `/produtos/estoque-baixo` | logado | Produtos com estoque no mínimo ou abaixo dele |
| GET | `/produtos/{id}` | logado | Busca por id |
| POST | `/produtos` | admin | Cria |
| PATCH | `/produtos/{id}` | admin | Altera (exceto o estoque) |
| DELETE | `/produtos/{id}` | admin | Exclui, se não houver movimentações |

**GET /produtos** aceita os parâmetros de query:

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `categoria_id` | inteiro | Só produtos da categoria |
| `fornecedor_id` | inteiro | Só produtos do fornecedor |
| `nome` | texto | Busca parcial no nome, sem diferenciar maiúsculas |

Exemplo: `GET /produtos?categoria_id=1&nome=lumin`

**GET /produtos/estoque-baixo** retorna os produtos em que `quantidade_em_estoque <= estoque_minimo`, ordenados do menor estoque para o maior. A comparação é feita no próprio SQL, sem carregar todos os produtos na aplicação. O produto que está exatamente no mínimo também aparece, porque já precisa de reposição.

**POST /produtos**

```json
{
  "nome": "Luminária de papel",
  "sku": "LUM-001",
  "preco_custo": "12.50",
  "preco_venda": "29.90",
  "estoque_minimo": 5,
  "categoria_id": 1,
  "fornecedor_id": 1
}
```

Resposta `201`:

```json
{
  "id": 1,
  "nome": "Luminária de papel",
  "sku": "LUM-001",
  "preco_custo": "12.50",
  "preco_venda": "29.90",
  "quantidade_em_estoque": 0,
  "estoque_minimo": 5,
  "data_cadastro": "2026-10-06T16:41:53.396298-03:00",
  "categoria_id": 1,
  "fornecedor_id": 1
}
```

Os preços usam `Numeric(10, 2)` no banco e são devolvidos como texto para não perder precisão com arredondamento de ponto flutuante.

Erros: `400` (campos inválidos ou preço negativo), `404` (categoria ou fornecedor não existe), `409` (SKU já cadastrado).

**PATCH /produtos/{id}** aceita qualquer subconjunto dos campos do POST. Se `quantidade_em_estoque` for enviado, ele é ignorado. Resposta `200`. Erros: `400`, `404`, `409`.

**DELETE /produtos/{id}** responde `204`. Erros: `404`, `409` (produto com movimentações).

### Movimentações

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/movimentacoes` | logado | Histórico, com filtros opcionais |
| GET | `/movimentacoes/{id}` | logado | Busca por id |
| POST | `/movimentacoes` | logado | Registra entrada ou saída |

**POST /movimentacoes**

```json
{ "produto_id": 1, "tipo": "saida", "quantidade": 3 }
```

`tipo` aceita `entrada` ou `saida`. `quantidade` precisa ser maior que zero. A data é preenchida pelo servidor.

Resposta `201`:

```json
{
  "id": 7,
  "produto_id": 1,
  "tipo": "saida",
  "quantidade": 3,
  "data": "2026-10-06T17:02:11.120934-03:00"
}
```

Erros: `400` (quantidade inválida ou estoque insuficiente), `404` (produto não existe).

Exemplo de estoque insuficiente:

```json
{ "status": 400, "mensagem": "Estoque insuficiente: disponível 2, solicitado 5." }
```

**GET /movimentacoes** retorna o histórico da mais recente para a mais antiga e aceita os parâmetros de query:

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `data_inicio` | data (`AAAA-MM-DD`) | A partir deste dia, inclusive |
| `data_fim` | data (`AAAA-MM-DD`) | Até este dia, inclusive |
| `fornecedor_id` | inteiro | Movimentações dos produtos deste fornecedor |
| `produto_id` | inteiro | Movimentações de um produto |
| `tipo` | `entrada` ou `saida` | Só um tipo |

Exemplo: `GET /movimentacoes?fornecedor_id=1&data_inicio=2026-10-01&data_fim=2026-10-31`

A movimentação não guarda o fornecedor. Ele é descoberto pelo produto, com um `JOIN` na tabela `produtos`.

Erros: `400` (data em formato inválido ou `data_inicio` depois de `data_fim`).

### Saúde

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/health` | público | Responde `{"status": "ok"}` se a API estiver no ar |

## Testes

Os testes usam um banco separado, porque apagam todos os dados entre um caso e outro. Por padrão o nome é o mesmo do `DATABASE_URL` com `_teste` no final:

```sql
CREATE DATABASE desafio_ecompjr_teste;
```

Para usar outro endereço, defina a variável de ambiente `TEST_DATABASE_URL`.

```bash
pytest -v
```

São 34 testes cobrindo o CRUD das entidades, as regras de exclusão, as consultas, os erros padronizados, as permissões por papel e o cenário de concorrência.

A cada push na `master` e em cada pull request, o GitHub Actions (`.github/workflows/ci.yml`) sobe um PostgreSQL, aplica as migrations, desfaz e reaplica todas para garantir que o `downgrade` também funciona, e roda os testes.

## Estrutura do projeto

```
app/
  main.py           cria a aplicação e registra as rotas
  config.py         lê as variáveis do .env
  database.py       conexão com o banco e sessão por requisição
  security.py       hash de senha, geração e validação do JWT, controle de papéis
  exceptions.py     exceções de domínio (não encontrado, conflito, regra de negócio...)
  errors.py         converte as exceções no formato padrão de erro
  criar_admin.py    script para criar o primeiro administrador
  models/           tabelas (SQLAlchemy)
  schemas/          formato de entrada e saída da API (Pydantic)
  services/         regras de negócio
  routers/          rotas HTTP
alembic/            migrations
tests/              testes automatizados
```

O projeto segue uma arquitetura em camadas. O router só lida com HTTP (recebe a requisição e devolve a resposta), o service concentra as regras de negócio e o model representa a tabela. Os services lançam exceções de domínio, como `NaoEncontrado` ou `Conflito`, sem saber nada de HTTP, e o `errors.py` traduz cada uma para o código de status correto.

Não criei uma camada de repositório separada porque a `Session` do SQLAlchemy já cumpre esse papel, e o desafio fixa o ORM e o banco. Uma interface de repositório com uma única implementação seria só uma camada a mais repassando chamadas.
