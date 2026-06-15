---
name: stephen-chow-skill
description: Analyze Stephen Chow films and broader Chinese-language absurdist comedy, diagnose comedy scenes, and develop original sketches, ads, short videos, characters, beat sheets, scripts, and directing notes without impersonating a living person or reproducing protected dialogue, characters, plots, voices, or likenesses. Use when users mention 周星驰, 星爷, Stephen Chow, 无厘头, 港式喜剧, absurdist comedy, comedy rewrites, joke diagnosis, comic escalation, or request a rights-aware work inspired by high-level comedic mechanisms.
---

# Stephen Chow Skill

Create original comedy through analyzable mechanisms. Treat Stephen Chow's films as subjects of criticism and research, never as a license to imitate his identity or reproduce protected expression.

## Route The Request

Classify the request before writing:

1. **Research**: answer factual or critical questions. Read `references/research-protocol.md` and `references/source-registry.json`.
2. **Diagnosis**: explain why supplied material does or does not work. Read `references/style-framework.md` and `references/evaluation-rubric.md`.
3. **Original creation**: create a new scene, script, ad, short video, character, or beat sheet. Read `references/creation-workflows.md`, `references/style-framework.md`, and `references/rights-and-safety.md`.
4. **Transformation**: rewrite user-provided text. Establish that the user supplied it, preserve only requested constraints, and apply the originality gate below.
5. **Identity or asset simulation**: read `references/rights-and-safety.md`; refuse impersonation, endorsement, face/voice cloning, or unauthorized continuation of protected stories. Offer an original alternative.

When a request combines modes, run them in that order. Do not invent citations, interviews, production history, creative intent, box-office figures, or quotations.

## Gather A Minimal Brief

Infer safe defaults when possible. Identify:

- format and target duration;
- audience, language, region, and platform;
- premise, product, or message that must survive the comedy;
- desired emotional landing;
- constraints and the user's rights to supplied material.

Ask a question only when a missing answer would materially change the deliverable or create legal risk.

## Build Original Comedy

Follow this sequence:

1. State the ordinary reality and the protagonist's sincere want.
2. Select two or three mechanisms from `references/style-framework.md`.
3. Create a beat sheet before dialogue: setup, rule, disruption, escalation, reversal, consequence, emotional return.
4. Replace recognizable names, worlds, props, powers, relationships, staging, and verbal patterns with independent choices.
5. Draft dialogue from character objectives. Do not start from remembered movie lines.
6. Add performance and visual directions only when the medium benefits.
7. Run the originality and quality gates.

For creative requests, normally return three materially different concepts before expanding one. If the user asks for a finished draft immediately, choose one concept and briefly name the mechanisms used.

## Enforce The Originality Gate

Reject or redirect output when it:

- presents the assistant as Stephen Chow or implies his participation or endorsement;
- clones or instructs cloning of his face, voice, signature, or identity without documented authorization;
- continues a recognizable film, character, universe, or scene without rights;
- reproduces substantial dialogue, subtitles, scripts, lyrics, or distinctive scene expression;
- merely swaps nouns in a known scene;
- markets an output as "official," "authentic," or "by Stephen Chow" without evidence.

Offer this alternative: analyze high-level mechanisms, then create a new premise, characters, setting, comic engine, language pattern, and ending.

For repository or batch workflows, run:

```powershell
python scripts/quote_guard.py --candidate output.txt --references rights-holder-material.txt
python scripts/evaluate_output.py --input output.txt --mode script
```

The first command requires lawfully obtained reference material supplied by the operator. Never bundle copyrighted subtitle or script corpora with this skill.

## Evaluate Before Delivery

Use the rubric in `references/evaluation-rubric.md`. Revise when any critical dimension is below 3/5 or when a hard-fail rule triggers.

Check:

- causal logic and character motivation;
- escalation rather than disconnected randomness;
- mechanism diversity and non-redundant variants;
- visual playability and platform fit;
- emotional return without forced sentiment;
- factual support and citation quality for research answers;
- identity, copyright, privacy, endorsement, and AI-labeling risks.

Separate fact from interpretation. Label uncertain claims and state when current web verification is required.

## Deliver Clearly

For research, provide: conclusion, evidence, interpretation, uncertainty, and sources.

For creation, provide: premise, mechanism choices, beat sheet or finished draft, performance/directing notes when useful, and a short originality note. Do not repeatedly invoke Stephen Chow's name in the generated work.

For refusals, identify the specific unsafe element in one sentence and immediately provide a workable original route.
