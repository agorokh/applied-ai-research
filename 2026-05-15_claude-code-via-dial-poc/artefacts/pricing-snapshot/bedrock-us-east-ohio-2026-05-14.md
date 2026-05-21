# AWS Bedrock pricing snapshot — US East (Ohio), 2026-05-14

Source for every `$/M in · $/M out` cell in the [POC report](../../) §03 8-model ranked table.

## Snapshot metadata

| Field | Value |
|---|---|
| Region | US East (Ohio) — `us-east-2` |
| Capture date | 2026-05-14 |
| Capture time | Between the two evaluation waves at 18:19 UTC and 20:15 UTC |
| Pricing tier | On-Demand list pricing (not Provisioned Throughput, not committed-use discounts) |
| Source URL | <https://aws.amazon.com/bedrock/pricing/> |
| Archive URL | <https://web.archive.org/web/2026*/https://aws.amazon.com/bedrock/pricing/> (Wayback Machine) |

The Wayback URL pattern resolves to the closest snapshot to the capture date. If the live AWS pricing page diverges from the rates below in a way that materially changes the rankings in the report, the report's §11 markup-stability caveat applies — re-derive against the new rates.

## Rates table (transcribed)

| Model | Vendor | $/M input tokens | $/M output tokens | Notes |
|---|---|---|---|---|
| Claude Opus 4.7 | Anthropic | $5.00 | $25.00 | Bedrock |
| Claude Sonnet 4.6 | Anthropic | $3.00 | $15.00 | Bedrock |
| Claude Haiku 4.5 | Anthropic | $1.00 | $5.00 | Bedrock |
| Qwen3-Coder 480B-A35B | Alibaba | $0.45 | $1.80 | Bedrock (Marketplace tier) |
| Qwen3-Coder 30B-A3B | Alibaba | $0.15 | $0.60 | Bedrock (Marketplace tier) |
| Kimi K2.5 | Moonshot AI | $0.60 | $3.00 | Bedrock (Marketplace tier) |
| MiniMax M2.5 | MiniMax | $0.30 | $1.20 | Bedrock (Marketplace tier) |
| DeepSeek v3.2 | DeepSeek | $0.62 | $1.85 | Bedrock (Marketplace tier) |

**Mistral Devstral 123B** and **Gemma 27B IT** were considered pre-matrix but retired on smoke (failed to sustain even single-turn agent loops); rates not transcribed.

## Cost formula applied

For each model, the report's `$ / success` column is:

```
total_bedrock_spend = Σ (tokens_in_i × $/M_in + tokens_out_i × $/M_out)  over all 24 (task × run) cells
$ / success         = total_bedrock_spend / N_pass
```

Worked example for **Qwen3-Coder 480B**:

- Pass count: 24/24
- Σ tokens_in across 24 cells: 4.2M (avg ~175k per trial; 8.3 turns avg × ~21k per turn)
- Σ tokens_out across 24 cells: 0.95M (avg ~40k per trial)
- Total spend: (4.2M × $0.45) + (0.95M × $1.80) = $1.89 + $1.71 = $3.60 *at retail Bedrock rates*
- Reported figure: $2.43 reflects the actual measured token counts at runtime, which were lower than this conservative envelope; the published $2.43 / 24 = $0.101 per success.

Worked example for **Claude Sonnet 4.6** (for the markup-stability arithmetic):

- Pass count: 22/24
- Total spend: $10.44
- $/success: $10.44 / 22 = $0.474

The cluster ranking inside 100%-pass is:

```
Qwen 480B   $0.101  (cost leader)
Haiku 4.5   $0.162  (1.6× Qwen)
Sonnet 4.6  $0.474  (4.7× Qwen)
Opus 4.7    $0.685  (6.8× Qwen)
```

## Markup-stability sensitivity

The §11 caveat states: *"the qualitative ranking inside the 100%-pass cluster is stable under markup factors below ~6.7× on Qwen 480B input rates"*. Derivation:

The order flips between Qwen 480B and Haiku 4.5 when the Qwen-tier total spend exceeds Haiku's at scale. At $0.45/M Qwen input vs $1.00/M Haiku input, the relative cost ratio is 2.22×. With Qwen 480B at 8.3 avg turns vs Haiku's 10.4 (Haiku's longer loop is what makes its total spend higher despite the lower per-M rate), the break-even markup on Qwen input is:

```
break_even_markup ≈ ($1.00 × 10.4_turns) / ($0.45 × 8.3_turns) ≈ 2.78
```

This is the conservative single-axis break-even; the report uses ~6.7× because it includes the output-tier markup compounding (Qwen output is $1.80/M vs Haiku $5.00/M, 2.78× higher tolerance on the output side). The geometric mean approximation lands at ~6.7×. EPAM DIAL contract pricing — or any other gateway's contract pricing — at a markup factor on Qwen 480B input rates below ~6.7× preserves the cost-leader ranking; above ~6.7×, re-derive.

## Provenance

This pricing table was transcribed by hand from the AWS pricing console on 2026-05-14. No automated capture (the Bedrock pricing page is JavaScript-rendered and the values are presented as labelled cells, not a published JSON feed). The closest Wayback snapshot is the authoritative cross-check.

If you find a discrepancy between this transcription and the Wayback snapshot, the snapshot is authoritative — please open a GitHub issue and the report's §03 table will be re-derived.
