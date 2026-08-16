# Evidence-Grounded Engineering Copilot

The copilot is a governed investigation workflow, not a chatbot with unrestricted access.

## Contract

1. Accept a precise engineering question.
2. Retrieve only approved structured evidence.
3. Preserve evidence IDs and source references.
4. Rank hypotheses with supporting and contradicting evidence.
5. Expose missing evidence.
6. Propose bounded actions.
7. Require human approval for workload, power, maintenance, or lot-disposition actions.
8. Store the decision and audit note.

The dependency-free reference implementation is `apps/local_platform/engineering_copilot.py`.

## Tool boundaries

Read tools: device state, operational twin, peer group, incident history, and monitor history.

Gated tools: redistribute workload, change a power limit, schedule maintenance, and quarantine a wafer lot.

Free-text model output is not accepted as sensor evidence. A production LLM may summarize retrieved evidence or translate the structured case into natural language, but the evidence and permission layers remain deterministic and auditable.

## Production extension

- Hybrid retrieval over monitor data, incident records, engineering specifications, test reports, and maintenance history.
- Knowledge graph for device/wafer/lot/tool/chamber/firmware/workload relationships.
- Evaluation set with expert-ranked causes, missing evidence, and safe next actions.
- Prompt-injection controls, tenant isolation, least-privilege credentials, and immutable audit logs.
- Abstention when evidence coverage or source quality is insufficient.
