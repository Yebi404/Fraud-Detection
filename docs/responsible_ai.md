# Responsible AI

- Privacy: IDs hashed/tokenized upstream; no PII stored by service.
- Fairness: Structural/temporal features only (no demographic attributes).
- Explainability: Reasons per score; ring visualization available via notebook artifacts.
- Transparency: Add audit logging at gateway (trace_id, request, response).
- Human-in-loop: Scores are advisory; analysts review before action.
