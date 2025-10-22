# 🐛 Debug Configuration Guide

Este guia mostra como configurar debug para o projeto FastAPI + Celery em containers Docker.

## 📋 Métodos Disponíveis

### Método 1: Remote Debug (Recomendado) 🚀

**Ideal para:** Debug completo com breakpoints, stepping, e variable inspection.

#### Passo a Passo:

1. **Pare os containers normais:**
   ```bash
   docker compose down
   ```

2. **Inicie os containers de debug:**
   ```bash
   docker compose -f docker-compose.debug.yml up --build
   ```

3. **Aguarde a mensagem no log:**
   ```
   ⏳ Waiting for debugger to attach...
   ```

4. **No VS Code:**
   - Abra o arquivo que quer debugar (ex: `backend/app/main.py`)
   - Coloque breakpoints clicando na margem esquerda (bolinhas vermelhas)
   - Vá para Run & Debug (`Ctrl+Shift+D` ou `Cmd+Shift+D`)
   - Selecione **"FastAPI Debug (Remote Attach)"**
   - Pressione `F5` ou clique no botão play ▶️

5. **Teste a API:**
   ```bash
   curl -X POST http://localhost:8060/tasks/slow?duration=5
   ```

6. **O debugger vai parar nos breakpoints!** 🎉

---

### Método 2: Debug Dentro do Container 🐳

**Ideal para:** Debug quando já está usando Dev Container.

#### Passo a Passo:

1. **Attach to Container:**
   - `Ctrl+Shift+P` → `Dev Containers: Attach to Running Container`
   - Selecione o container backend

2. **Pare o processo FastAPI:**
   ```bash
   # Dentro do container
   pkill -f uvicorn
   ```

3. **No VS Code (dentro do container):**
   - Vá para Run & Debug (`Ctrl+Shift+D`)
   - Selecione **"FastAPI Debug (Container)"**
   - Pressione `F5`

---

### Método 3: Debug de Tarefas Celery 🔄

**Para debugar tasks Celery:**

1. **Inicie containers de debug:**
   ```bash
   docker compose -f docker-compose.debug.yml up --build
   ```

2. **Pare o worker Celery:**
   ```bash
   docker compose -f docker-compose.debug.yml stop worker
   ```

3. **Attach to Container backend-debug:**
   - VS Code → Dev Containers → Attach to Running Container
   - Selecione `learning_python_fastapi_celery-backend-debug-1`

4. **No VS Code (dentro do container):**
   - Abra `backend/app/tasks.py`
   - Coloque breakpoints nas funções de task
   - Run & Debug → **"Celery Worker Debug (Container)"**
   - Pressione `F5`

5. **Teste criando uma task:**
   ```bash
   curl -X POST http://localhost:8060/tasks/slow?duration=10
   ```

---

## 🔧 Configurações Incluídas

### Debug Configurations (`.vscode/launch.json`)

1. **FastAPI Debug (Container)** - Debug direto dentro do container
2. **FastAPI Debug (Remote Attach)** - Attach remoto na porta 5678
3. **Celery Worker Debug (Container)** - Debug de tarefas Celery
4. **Python: Current File (Container)** - Debug de arquivo específico
5. **Pytest Debug (Container)** - Debug de testes

### Docker Compose Debug (`docker-compose.debug.yml`)

- **backend-debug**: FastAPI com debugpy habilitado na porta 5678
- **worker**: Celery worker com log debug
- **flower**: Monitoring normal
- **db**: PostgreSQL normal
- **rabbitmq**: RabbitMQ normal

### Dev Container (`.devcontainer/devcontainer.json`)

- **debugpy extension** incluída automaticamente
- **Python debugging** pré-configurado

---

## 🎯 Exemplos Práticos

### Debug de Endpoint FastAPI

1. **Coloque breakpoint em `main.py`:**
   ```python
   @app.post("/tasks/slow")
   def enqueue_slow_task(duration: int = 10):
       # 🔴 Breakpoint aqui
       task = slow_task.delay(duration)
       return TaskEnqueueResponse(...)
   ```

2. **Inicie debug remoto**

3. **Faça request:**
   ```bash
   curl -X POST http://localhost:8060/tasks/slow?duration=5
   ```

4. **Debugger para no breakpoint!**

### Debug de Task Celery

1. **Coloque breakpoint em `tasks.py`:**
   ```python
   @celery_app.task(name="app.tasks.slow_task")
   def slow_task(duration: int = 10) -> dict:
       # 🔴 Breakpoint aqui
       import time
       time.sleep(duration)
       return {"message": f"Task completed after {duration} seconds"}
   ```

2. **Inicie Celery worker em debug**

3. **Crie uma task**

4. **Debugger para quando a task executar!**

### Debug de Teste

1. **Coloque breakpoint em `test_api.py`:**
   ```python
   def test_enqueue_task():
       response = client.post("/tasks/", json={"content": "Test message"})
       # 🔴 Breakpoint aqui
       assert response.status_code == 202
   ```

2. **Use "Pytest Debug (Container)"**

3. **Debugger para durante o teste!**

---

## 🚨 Troubleshooting

### Debug não conecta

1. **Verifique se a porta 5678 está aberta:**
   ```bash
   docker compose -f docker-compose.debug.yml ps
   # Deve mostrar 5678:5678 no backend-debug
   ```

2. **Verifique logs do container:**
   ```bash
   docker compose -f docker-compose.debug.yml logs backend-debug
   ```

3. **Restrte containers debug:**
   ```bash
   docker compose -f docker-compose.debug.yml down
   docker compose -f docker-compose.debug.yml up --build
   ```

### Breakpoints não funcionam

1. **Verifique path mappings:** Local root deve ser `${workspaceFolder}/backend`
2. **Desabilite "justMyCode"** nas configurações
3. **Verifique se o arquivo está sendo executado** (não apenas importado)

### Performance lenta

1. **Use debug apenas quando necessário**
2. **Para produção, use containers normais:**
   ```bash
   docker compose up -d
   ```

---

## 📚 Recursos Úteis

### Comandos Debug

```bash
# Iniciar debug environment
docker compose -f docker-compose.debug.yml up --build

# Ver logs de debug
docker compose -f docker-compose.debug.yml logs -f backend-debug

# Parar debug environment
docker compose -f docker-compose.debug.yml down

# Voltar para ambiente normal
docker compose up -d
```

### VS Code Shortcuts

- `F5` - Start/Continue debugging
- `F10` - Step over
- `F11` - Step into
- `Shift+F11` - Step out  
- `Shift+F5` - Stop debugging
- `Ctrl+Shift+D` - Open Debug panel

### Variáveis de Ambiente para Debug

```bash
# No container debug
PYTHONPATH=/app
DEBUG=true
LOG_LEVEL=debug
```

---

## 🎉 Conclusão

Agora você tem **4 formas diferentes** de fazer debug:

1. **🚀 Remote Attach** - Mais flexível, funciona de fora do container
2. **🐳 Container Debug** - Quando já está no Dev Container  
3. **🔄 Celery Debug** - Para debugar tarefas assíncronas
4. **🧪 Test Debug** - Para debugar testes

**Escolha o método que melhor se adapta ao seu workflow!**

Happy debugging! 🐛✨