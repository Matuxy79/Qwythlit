# Qwythlit Dragon Stub — Agent Handoff

## Intent

Use the supplied rainbow dragon artwork as a **visual metaphor for Qwythlit's retrieval pipeline**:

- dragon body = synthesis / context core
- wing span = retrieval fan-out
- orbiting UI nodes = sources and processing stages
- rainbow breath = evidence stream / grounded response
- particles = retrieved chunks or citations
- trace list = observable ranked retrieval results

The dragon image itself is intentionally not cut into fake sprite parts. Motion is created with CSS around the intact artwork so the demo is low-risk and easy to port.

## Run

```bash
npm install
npm run dev
```

## Integration target

Port `src/App.jsx` and `src/styles.css` into the existing Qwythlit frontend.

Replace the stub `CHUNKS` and idle/active toggle with application state:

- retrieval started -> `active = true`
- chunk search results -> `CHUNKS`
- rerank scores -> `score`
- generation complete -> transition core state from `SYNTHESIZING` to `ANSWER READY`

## Suggested production component split

- `QwythlitDragonScene`
- `RetrievalNode`
- `ContextParticleField`
- `RetrievalTrace`
- `QueryIgnitionControl`

## Keep

- `prefers-reduced-motion`
- code-native labels and controls
- the image as a replaceable asset
- animation driven by real retrieval lifecycle events

## Avoid

- tying data logic to animation timing
- animating hundreds of DOM particles
- using the dragon graphic as a functional status indicator without an accessible textual equivalent
- turning the effect into a permanent full-screen GPU tax

## Nice next step

Drive the scene from a tiny finite-state machine:

`idle -> retrieving -> reranking -> synthesizing -> complete -> error`

Each state can alter node glow, line flow, breath intensity and trace visibility.
