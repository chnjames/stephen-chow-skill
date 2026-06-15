# Research Protocol

## Evidence Order

1. Statutes, regulators, courts, and official standards.
2. Rightsholders, film archives, award bodies, distributors, and contemporaneous credits.
3. Peer-reviewed scholarship and books from reputable academic publishers.
4. Recorded interviews and established journalism.
5. Platform pages and analytics captured with date and method.
6. Encyclopedias, fan databases, social posts, and search snippets only as leads.

## Claim Discipline

- Attach a source to every externally verifiable claim that may have changed or may be disputed.
- Use exact dates for laws, releases, awards, metrics, and account status.
- Never infer creative intent from the finished film alone. Label formal interpretation as interpretation.
- Do not treat box-office databases as interchangeable; state currency, territory, gross type, and retrieval date.
- Do not claim "whole-web" coverage. State search scope, languages, source classes, date range, and blind spots.
- Cross-check high-impact claims with two independent sources when possible.

## Source Maintenance

Run:

```powershell
python scripts/source_validator.py references/source-registry.json
```

Re-verify legal and platform-policy entries before each public release and at least every 90 days. Re-verify stable historical sources annually or when challenged.

## Research Answer Format

```text
Conclusion
Verified facts
Interpretation
Uncertainty and conflicting evidence
Sources with access dates
```

Do not quote more than needed. Paraphrase criticism and scholarship, preserving attribution.
