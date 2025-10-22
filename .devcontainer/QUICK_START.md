# 🚀 Quick Start: Dev Container

## Como Usar as Extensões Persistentes

### Método 1: Attach to Running Container (Recomendado)

1. **Certifique-se que os containers estão rodando:**
   ```bash
   docker compose up -d
   ```

2. **No VS Code:**
   - Pressione `Ctrl+Shift+P` (ou `Cmd+Shift+P` no Mac)
   - Digite: `Dev Containers: Attach to Running Container`
   - Selecione: `learning_python_fastapi_celery-backend-1`

3. **Aguarde a instalação das extensões** (primeira vez ~2 minutos)

4. **Pronto!** Todas as extensões estarão instaladas automaticamente:
   - Python
   - Black formatter
   - Pylint & Flake8
   - GitLens
   - Docker
   - REST Client
   - E muitas outras...

### Método 2: Reopen in Container

1. **Abra o projeto no VS Code**
2. **Pressione `Ctrl+Shift+P`**
3. **Digite:** `Dev Containers: Reopen in Container`
4. **Selecione:** `FastAPI + Celery Backend`

## ✨ O Que Você Ganha

### Extensões Automáticas
- ✅ **Python** - Suporte completo ao Python
- ✅ **Black** - Formatação automática
- ✅ **Pylint/Flake8** - Linting em tempo real
- ✅ **GitLens** - Git avançado
- ✅ **REST Client** - Testar APIs direto no VS Code
- ✅ **Docker** - Gerenciar containers
- ✅ **PostgreSQL** - Conectar ao banco
- ✅ **Jupyter** - Notebooks Python

### Configurações Automáticas
- ✅ **Python interpreter** configurado
- ✅ **Formatação automática** ao salvar
- ✅ **Organização de imports** automática
- ✅ **Linting habilitado**
- ✅ **Testing (pytest)** configurado
- ✅ **Port forwarding** (8060) automático

## 🧪 Testando

Depois de conectar, teste no terminal integrado:

```bash
# Formatar código
black app/

# Verificar linting
flake8 app/

# Rodar testes
pytest

# Verificar dependências
pip list

# Ver Python version
python --version
```

## 🔗 Links Rápidos (dentro do container)

- **FastAPI Docs:** http://localhost:8060/docs
- **Flower:** http://localhost:5555
- **RabbitMQ:** http://localhost:15672

## 🛠️ Personalizações

Para adicionar mais extensões, edite `.devcontainer/devcontainer.json`:

```json
"extensions": [
  "ms-python.python",
  "sua-nova-extensao-aqui"
]
```

## ❓ Problemas Comuns

### Extensões não instalam
1. Verifique se está conectado ao container
2. Aguarde alguns minutos na primeira vez
3. Tente desconectar e reconectar

### Python não encontrado
1. `Ctrl+Shift+P` → `Python: Select Interpreter`
2. Escolha `/usr/local/bin/python`

### Porta 8060 não funciona
1. Verifique a aba "Ports" no terminal
2. Se necessário, adicione manualmente a porta 8060

---

**Agora você tem um ambiente de desenvolvimento completo e consistente! 🎉**