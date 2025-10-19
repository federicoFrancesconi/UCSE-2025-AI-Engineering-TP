# UCSE-2025-AI-Engineering-TP

Trabajo Práctico Integrador de la materia Tópicos Avanzados de IA de 2025 en UCSE.

## 📋 Descripción del Proyecto

Sistema de agente AI basado en LangGraph que traduce preguntas en lenguaje natural a consultas SQL para una base de datos de plataforma de streaming.

## 🏗️ Estructura del Proyecto

```
UCSE-2025-AI-Engineering-TP/
├── agent/                          # Módulo del Agente AI
│   ├── agent.py                   # Implementación LangGraph
│   ├── sql_tool.py                # Herramienta SQL
│   ├── main.py                    # Interfaz CLI
│   ├── test_agent.py              # Script de prueba
│   └── .env.example               # Plantilla de configuración
├── database/                       # Módulo de Base de Datos
│   ├── create_streaming_tables.sql
│   ├── insert_sample_data.sql
│   ├── generate_fake_data.py
│   └── README.md
├── docs/                          # Documentación
│   ├── architecture/              # Diagramas de arquitectura
│   ├── agent-readme.md           # Documentación del agente
│   ├── quickstart.md             # Guía de inicio rápido
│   └── implementation.md         # Detalles de implementación
├── requirements.txt              # Dependencias del proyecto
├── .gitignore                   # Configuración Git
└── README.md                    # Este archivo
```

## 🚀 Inicio Rápido

### Prerrequisitos

1. **PostgreSQL** instalado y corriendo
2. **Ollama** instalado con los modelos:
   - `sqlcoder:7b` - Para generación de SQL
   - `llama3.2:3b` - Para respuestas conversacionales
3. **Python 3.10+**

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/federicoFrancesconi/UCSE-2025-AI-Engineering-TP.git
cd UCSE-2025-AI-Engineering-TP

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
psql -U postgres -c "CREATE DATABASE streaming"
psql -U postgres -d streaming -f database/create_streaming_tables.sql
psql -U postgres -d streaming -f database/insert_sample_data.sql

# 5. Configurar variables de entorno
cd agent
cp .env.example .env
# Editar .env con tus credenciales

# 6. Ejecutar el agente
python main.py
```

## 📚 Documentación

- **[Guía de Inicio Rápido](docs/quickstart.md)** - Configuración y uso básico
- **[Documentación del Agente](docs/agent-readme.md)** - Guía completa del agente AI
- **[Detalles de Implementación](docs/implementation.md)** - Información técnica detallada
- **[Diagramas de Arquitectura](docs/architecture/)** - Diseño del sistema

## 🎯 Características

- ✅ Traducción de lenguaje natural a SQL
- ✅ Workflow multi-nodo con LangGraph
- ✅ Validación de SQL (solo queries SELECT)
- ✅ Conocimiento del esquema de base de datos
- ✅ Manejo de errores robusto
- ✅ Salida de tablas formateadas
- ✅ Respuestas conversacionales
- ✅ Logging comprehensivo

## 💡 Ejemplo de Uso

```
💬 Your question: ¿Cuántos usuarios tenemos registrados?

🤔 Thinking...

======================================================================

📝 Generated SQL:
   SELECT COUNT(*) FROM usuarios

🤖 Response:
   We currently have 20 registered users on our platform.

📊 Query Results:
   ✓ Query returned 1 row(s):
   +-------+
   | count |
   +=======+
   |    20 |
   +-------+

======================================================================
```

## 🔧 Stack Tecnológico

- **Orquestación**: LangGraph 0.2.28
- **Framework LLM**: LangChain 0.3.1
- **Modelos**:
  - Ollama sqlcoder:7b (generación SQL)
  - Ollama llama3.2:3b (conversación)
- **Base de Datos**: PostgreSQL
- **Parsing SQL**: sqlparse
- **Formateo**: tabulate

## 🛡️ Seguridad

- Solo queries SELECT (acceso de solo lectura)
- Validación de SQL antes de ejecución
- Prevención de inyección SQL
- Bloqueo de operaciones peligrosas

## 📝 Licencia

Proyecto académico - UCSE 2025 - Tópicos Avanzados de IA

## 👥 Autor

Federico Francesconi

---

Para más información, consulta la [documentación completa](docs/).

