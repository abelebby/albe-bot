# ALBE BOT

An offline troubleshooting chatbot for Albe Lestari's engineers and technicians, adapted from [Open WebUI](https://github.com/open-webui/open-webui) v0.11.4 (base commit `8bd8b4f`).

The current prototype focuses on **raw-water clarification**. It retrieves approved company handbook, product-sheet and safety-sheet passages from a local database and uses a local Ollama model to explain them. Each installation runs independently on one machine. New chats start fresh; follow-ups retain context within their own chat.

## Current implementation

- Branded chat interface with ALBE BOT identity and a fixed `qwen3:1.7b` model; model selection and starter suggestions are hidden.
- Local Ollama inference and `nomic-embed-text:v1.5` embeddings; embedded Chroma and BM25/vector retrieval.
- 130 procedure-sized source records keep applicability, roles, examples and original/SPM references together. Source references distinguish original evidence from derivative explanations and editorial notes.
- Deterministic arithmetic for supported product-mass and w/v jar-test calculations.
- Selected observed-error checks, one correction attempt, and source excerpts when a detected contradiction persists.

The small model still makes interpretation errors. This is a development prototype; broader technical accuracy, multilingual answers and performance on 8 GB CPU-only laptops remain unvalidated. Training has not been performed. Topic-based source records are implemented; stronger-model evaluation remains pending.

## Local development

Use Python 3.12 and Node.js 22. Install [Ollama](https://ollama.com/) and provision the models while internet is available:

```sh
ollama pull qwen3:1.7b
ollama pull nomic-embed-text:v1.5
python3.12 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-local-rag.txt
npm ci
BUILD_SOURCEMAPS=false NODE_OPTIONS=--max-old-space-size=8192 npm run build
cp .env.elbe.example .env
./start-local.sh
```

Open http://127.0.0.1:8080/. Ollama must be running locally on port 11434. Stop the server with Ctrl+C in its terminal. The larger frontend build memory allowance is for a 16 GB development machine, not an 8 GB runtime claim. This is a source checkout, not an installation package.

Authentication is deferred and disabled in this prototype. The launcher binds to localhost. The example configuration disables cloud AI, web search, plugins, cross-chat memory and telemetry. Initial provisioning requires downloads; the intended document-answering flow uses local resources afterwards.

## Approved company documents

**PDFs, extracted content, indexes, chat history, model weights and secrets are not included in this repository.** Keep them in ignored local directories. The compilation tooling and expected source filenames are documented in [albe-rag/README.md](albe-rag/README.md).

Existing installations retain settings and model customisations in `backend/data/`. Changing `.env` does not necessarily override settings already persisted there. Use the deployment script after preparing sources to configure the ALBE BOT document collection.

## Checks

From this repository:

```sh
.venv/bin/python albe-rag/tests/test_source_rag.py
.venv/bin/python albe-rag/tests/test_topics.py
```

The targeted tests cover calculator bounds, explicit inputs, stock basis, within-chat retrieval context, observed-error checks and source-bound calculator rendering. They do not establish complete treatment accuracy. Local testing also exercised retrieval and calculations with backend external network access blocked; that is not a physically disconnected-laptop test.

## Upstream and licence

The upstream history, licence and notices are retained. See [LICENSE](LICENSE) and [the upstream README](docs/UPSTREAM-README.md). Branding and distribution conditions remain governed by that licence.

Inherited workflows are retained under `.github/upstream-workflows/` rather than enabled as automatic Docker/PyPI releases in this private development repository.
