# Local company-document tooling

This directory versions code and prompt configuration. Company documents and generated knowledge remain local and are ignored by Git.

Place the reviewed PDFs under `albe-rag/documents/`, or set `ALBE_DOCUMENT_DIR` to their local directory. The current compilation expects:

- Field Service Handbook Version 6.pdf
- Field Service Handbook - SPM Friendly Edition.pdf
- ABL- CF 1220 2024.pdf
- ABL-Cestfloc 1833 - MSDS (1).pdf
- ABL-PDV Salt.pdf
- CF 1311 PDS - 260928.pdf
- CF 1333 PDS - 260929.pdf
- CF 1490 PDS - 260929.pdf
- SODA ASH DENSE SDS - 2023.pdf

These page mappings and coverage notes refer to the reviewed editions. Recheck them before accepting replacement/revised PDFs.

Run from the repository root after installing backend dependencies:

```sh
.venv/bin/python albe-rag/prepare_sources.py
.venv/bin/python albe-rag/compile_sources.py
.venv/bin/python albe-rag/build_rag.py
.venv/bin/python albe-rag/build_topics.py
```

Start ALBE BOT in another terminal, then:

```sh
.venv/bin/python albe-rag/deploy_rag.py
```

Deployment configures the local knowledge collection and current model profile, retaining prior file versions and taking a private database backup. The dummy `admin@localhost` sign-in values target Open WebUI's authentication-disabled prototype branch; they are not credentials for a production account. This script must be adapted when authentication is introduced.

The source compilation covers seven original handbook pages relevant to raw-water treatment, 32 supplementary product-document pages, and six SPM explanation pages. The active topic representation contains 130 records, splitting independent handbook procedures, product PDS fields, and numbered SDS sections. Continued SDS sections retain their page references together. The SPM edition is derivative evidence, not independent approval. Company source content is reference data, not instructions to execute.

The initial GitHub commit preserves the page-based baseline; the next commit implements the topic-level representation. Review notes remain separate from original excerpts, and the current model still requires accuracy evaluation. Existing local source-review reports and experiments are outside this repository and have not been uploaded.

Verification: `tests/test_topics.py` checks the locally compiled evidence boundaries. `topic_live_check.py` exercises intake, the palm-oil raw-water scenario, product facts and supported calculations against the running app. Results stay under ignored `review/`.
