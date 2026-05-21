# Rubric file format

Two YAML files plus one tabulation spreadsheet, total under 100 lines of structured content. The schemas below are the minimum that supports a reproducible matrix row; extend with your own provenance fields as needed.

## File 1: pinned corpus list

`smoke_corpus.yml`: the explicit file list ingested for every model row. Glob patterns are not used; the matrix needs the same bytes for every row.

```yaml
version: 1
pinned_at: "2026-04-28"
notes: "Mixed-prose Markdown notes; 5 pages average; people, projects, decisions, dates as implicit entity types."
files:
  - relative/path/to/document-001.md
  - relative/path/to/document-002.md
  # ... 20 entries
```

## File 2: canary queries with expected references

`canary_queries.yml`: the 6 queries the rubric runs in each of 4 retrieval modes. Each query carries an `expected_refs` block that names what a passing retrieval must surface.

```yaml
version: 1
pinned_at: "2026-04-28"
queries:
  - id: q1_single_entity_recall
    shape: single-entity recall
    query: "what does the corpus say about <ENTITY_NAME>"
    expected_refs:
      - file: relative/path/to/document-013.md
        section: "## <SECTION_HEADING>"
        why: "Only place ENTITY_NAME is defined."
  - id: q2_cross_document_synthesis
    shape: cross-document synthesis
    query: "what is the relationship between <ENTITY_A> and <ENTITY_B>"
    expected_refs:
      - file: relative/path/to/document-007.md
        section: null
        why: "Names ENTITY_A in context of <PROJECT>."
      - file: relative/path/to/document-019.md
        section: null
        why: "Names ENTITY_B as <PROJECT>'s downstream consumer."
  # ... 4 more entries covering shapes 3-6 from the README
```

The `expected_refs` block is what makes scoring deterministic. A `pass` is "returned context includes at least one expected_refs entry by name or recognisable paraphrase." A `marginal` is "returned context cites a related file or section in the same neighbourhood but not the named one." A `fail` is "no expected_refs entry surfaces."

## File 3: tabulation

`smoke_results.csv`: one row per model, columns matching the matrix in the report.

```csv
model,provider,runtime,docs_ingested,chunks_total,ent_per_doc,rel_per_doc,rel_per_ent,pass,marginal,fail,measured_cost_usd
gemini-2.5-flash,google,openrouter,20,82,82.5,95.0,1.15,24,0,0,4.10
claude-sonnet-4.6,anthropic,openrouter,20,82,40.8,58.4,1.43,22,0,2,6.40
openai-gpt-4o-mini,openai,openrouter,150,615,17.1,17.8,1.04,19,3,2,0.30
# ... one row per model row in the matrix
```

The `measured_cost_usd` column is the provider's invoiced charge for the 20-document subset ingest, recorded at run time. Empty for local rows.

## Inter-rater honesty (optional but recommended)

If you have a second scorer available, ship one more file:

```csv
query_id,mode,scorer_1,scorer_2,agree
q1_single_entity_recall,naive,pass,pass,true
q1_single_entity_recall,local,pass,marginal,false
# ... 24 entries per model, second scorer fills in column scorer_2
```

A simple `agree` rate across the 24 cells is the inter-rater reliability number. Under 80% means the rubric is too loose and the cell definitions need tightening before the matrix is comparable across replicators. The operator's matrix in the report did not run this check; a second-scorer pass on the matrix would be the single highest-value re-measurement.
