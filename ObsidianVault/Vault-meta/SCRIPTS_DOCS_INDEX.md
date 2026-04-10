---
title: "Scripts folder documentation index"
tags: ["type/moc", "status/verified", "domain/harness"]
---

# Scripts folder documentation index

Markdown under `scripts/` is **code-adjacent** (vault tooling, RAG, tests). It is **excluded** from bulk YAML tag scans per [[00_HARNESS_VAULT_SCHEMA]]; use this MOC for navigation and graph hub-and-spoke links.

**Campaign pipeline outputs (TTRPG staging):** [[Campaigns/_rag_outputs/MOC_RAG_Outputs]] · [[Campaigns/README_workflow]]

## Configuration and operations

- [[scripts/CONFIGURATION_GUIDE]] — feature flags, OCR, AI summarization, long-term options
- [[scripts/DEPENDENCY_INSTALLATION]] — environment setup
- [[scripts/MIGRATION_GUIDE]] — migrations
- [[scripts/RUNBOOK]] — operations
- [[scripts/TROUBLESHOOTING]]
- [[scripts/API_DOCUMENTATION]]

## RAG pipeline and ingestion research

- [[scripts/BEST_PRACTICES_RESEARCH]] — PDF / Obsidian ingestion practices
- [[scripts/AI_DATA_NAMESPACES]]
- [[scripts/docs/RAG_VERIFICATION_FINDINGS]]
- [[scripts/docs/RAG_FEATURE_COMPLETENESS]]
- [[scripts/docs/ERROR_MONITORING_AND_KNOWN_ISSUES]]
- [[scripts/WORKFLOW_GAPS_ANALYSIS]]
- [[scripts/TASK_DECOMPOSITION]] — script-side task decomposition doc (distinct from `Campaigns/` YAML)

## Feature inventory and roadmap

- [[scripts/FEATURE_INVENTORY]] · [[scripts/FEATURE_MATRIX]] · [[scripts/FEATURE_GAP_ANALYSIS]]
- [[scripts/FEATURE_TRACKING_GUIDE]] · [[scripts/FEATURE_TRACKING_SCHEMA]]
- [[scripts/FEATURE_PRIORITIZATION]] · [[scripts/FEATURE_AUDIT_SPREADSHEET]]
- [[scripts/FEATURE_DEPENDENCY_GRAPH]] · [[scripts/FEATURE_COVERAGE_BASELINE]]
- [[scripts/TARGET_FEATURE_SPECIFICATION]] · [[scripts/TARGET_FEATURES_ACCEPTANCE_CRITERIA]]
- [[scripts/MISSING_FEATURES_ANALYSIS]] · [[scripts/MVP_STATUS]] · [[scripts/IMPLEMENTATION_ROADMAP]]
- [[scripts/LONG_TERM_ENHANCEMENTS]] · [[scripts/LTE_IMPLEMENTATION_SUMMARY]]

## Integration and automation

- [[scripts/INTEGRATION_POINTS]] · [[scripts/INTEGRATION_OPPORTUNITIES]]
- [[scripts/AUTOMATION_ASSESSMENT]] · [[scripts/EXTENSIBILITY_EVALUATION]]
- [[scripts/COMPARISON_SUMMARY]]

## Implementation history and reports

- [[scripts/PHASE_1_IMPLEMENTATION_SUMMARY]] · [[scripts/PHASE_2_IMPLEMENTATION_SUMMARY]]
- [[scripts/FIRST_WAVE_COMPLETION_SUMMARY]] · [[scripts/IMPROVEMENTS_SUMMARY]]
- [[scripts/OLLAMA_MIGRATION_SUMMARY]] · [[scripts/PERFORMANCE_REPORT]]
- [[scripts/TEST_RESULTS]]

## Tests (markdown)

- [[scripts/tests/README]] · [[scripts/tests/TESTING_IMPLEMENTATION_SUMMARY]] · [[scripts/tests/TEST_FAILURE_ROOT_CAUSES]]

> Generated cache under `scripts/.pytest_cache/` is not indexed here.

## See also

- [[00_HARNESS_VAULT_SCHEMA]] — why `scripts/**` is out of bulk tag enforcement
- [[GRAPH_VIEWS]] — filter `path:scripts` when focusing this tree
