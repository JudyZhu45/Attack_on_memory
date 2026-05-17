# AgentMemoryCTF

AgentMemoryCTF 是一个用于测试 AI Agent 记忆系统安全性的 CTF 项目。项目提供 5 个攻击关卡，覆盖记忆泄露、记忆投毒和结构一致性破坏，并支持对 `mem0` 与 `Hindsight` 两类记忆后端进行实验。

## 项目内容

- `api/`：FastAPI 后端，提供关卡、健康检查和攻击提交接口。
- `web/`：Next.js 前端，提供本地 CTF 操作界面。
- `targets/`：记忆系统适配层，包括 `mem0` 和 `Hindsight`。
- `attacks/levels/`：L1-L5 攻击关卡定义。
- `defenses/`：输入过滤、写入验证、输出分类和 consolidation guard 等防御模块。
- `experiments/`：baseline 与 ablation 实验脚本。
- `scripts/`：烟雾测试、报告和单次攻击脚本。
- `docs/`：攻击分类、API 约定和产品研究计划。

## 环境要求

- Python 3.11 或更高版本，推荐 Python 3.12。
- Node.js 22 或更高版本。
- Docker 和 Docker Compose。
- OpenAI API Key：`mem0` 和 Hindsight Docker 服务会使用它。
- Anthropic API Key：LLM judge 和部分防御模块会使用它。

## 本地启动

### 1. 克隆并安装 Python 依赖

```bash
git clone <repo-url>
cd agentMemoryCTF
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

然后编辑 `.env`：

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
MEM0_TELEMETRY=False
HINDSIGHT_ENDPOINT=http://localhost:8888
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. 启动 Hindsight

```bash
docker compose up hindsight
```

Hindsight 默认监听：

- API: `http://localhost:8888`
- 额外服务端口: `9999`

### 4. 启动后端 API

新开一个终端：

```bash
source venv/bin/activate
uvicorn api.server:app --reload --port 8000
```

健康检查：

```bash
curl http://localhost:8000/api/health
```

### 5. 启动前端

新开一个终端：

```bash
cd web
npm install
npm run dev
```

打开 `http://localhost:3000`。

## Docker 启动

准备 `.env`：

```bash
cp .env.example .env
```

填入至少这些变量：

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

然后启动全套服务：

```bash
docker compose up --build
```

服务地址：

- 前端：`http://localhost:3000`
- 后端 API：`http://localhost:8000`
- Hindsight：`http://localhost:8888`

停止服务：

```bash
docker compose down
```

如果需要清空 Hindsight 的 Docker 数据卷：

```bash
docker compose down -v
```

## 运行测试和实验

测试 mem0：

```bash
python scripts/test_mem0.py
```

测试 Hindsight：

```bash
python scripts/test_hindsight.py
```

运行 mock baseline，不会调用真实 LLM：

```bash
python experiments/run_baseline.py
```

运行 live baseline，会调用真实后端和 LLM：

```bash
python experiments/run_baseline.py --live
```

实验结果默认写入 `experiments/results/`。该目录已在 `.gitignore` 中忽略，适合保存本地运行产物。

## API

后端默认运行在 `http://localhost:8000`：

- `GET /api/health`：检查 API、mem0、Hindsight 是否可用。
- `GET /api/levels`：返回 L1-L5 关卡信息。
- `POST /api/attack`：提交一次攻击尝试。

更多接口约定见 [docs/api_spec.md](docs/api_spec.md)。

## 上传仓库前建议

确认不要提交真实密钥：

```bash
git status
```

应该提交的配置文件包括：

- `.env.example`
- `requirements.txt`
- `Dockerfile`
- `web/Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

不应该提交：

- `.env`
- `venv/`
- `web/node_modules/`
- `web/.next/`
- 实验输出和本地结果文件

## 技术栈

- Backend: Python, FastAPI, Uvicorn, Pydantic
- Memory Targets: mem0, Hindsight
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Experiments: pandas, matplotlib, numpy
- LLM/Judge: Anthropic SDK

## 参考文档

- [docs/attack_taxonomy.md](docs/attack_taxonomy.md)
- [docs/api_spec.md](docs/api_spec.md)
- [docs/product_research_plan.md](docs/product_research_plan.md)
