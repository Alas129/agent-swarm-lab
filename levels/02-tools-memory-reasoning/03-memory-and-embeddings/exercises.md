# Exercises — Memory & embeddings

## 1. See the toy embedder's limit
Add the fact "The red planet's satellites are small and irregular." Then query
"moons of Mars". Does it rank above unrelated facts? Now query using *only* synonyms the
facts don't contain. Explain, in terms of word overlap, why recall fails.

## 2. Cosine by hand
Compute `cosine([1,0,0], [1,0,0])`, `cosine([1,0,0],[0,1,0])`, and
`cosine([1,1,0],[1,0,0])` on paper, then check against the code. Why is the middle one 0?

## 3. Top-k and thresholds
`recall` filters out `score == 0`. Add a `min_score` threshold and a sensible `k`. What
breaks if you set `k` larger than the number of stored facts?

## 4. Chunking
Real documents are long. Add a `remember_document(text)` that splits text into ~1–2
sentence chunks before storing each. Why is chunk size a quality/cost trade-off?

## 5. Swap in a real embedder
Read the [Anthropic embeddings docs](https://platform.claude.com/docs/en/build-with-claude/embeddings).
Write a `VoyageEmbedder` with the same `embed(text)` interface (guarded so it no-ops
without `VOYAGE_API_KEY`). Confirm `VectorStore` works unchanged — that's the payoff of the
interface.

## Stretch
Combine short- and long-term memory: a chat agent that keeps the last N turns *and*
writes durable facts to `LongTermMemory`, recalling relevant ones into each prompt. This is
the memory architecture behind most production assistants.
