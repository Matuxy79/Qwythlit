import { useMemo, useState } from "react";
import {
  Activity,
  Database,
  Flame,
  Network,
  Search,
  Sparkles,
} from "lucide-react";

const NODES = [
  { id: "docs", label: "Documents", x: 11, y: 32, icon: Database },
  { id: "retrieval", label: "Retrieve", x: 24, y: 74, icon: Search },
  { id: "rerank", label: "Rerank", x: 77, y: 19, icon: Network },
  { id: "context", label: "Context", x: 86, y: 64, icon: Sparkles },
];

const CHUNKS = [
  { id: "c-17", title: "beamline-notes.md", score: 0.96 },
  { id: "c-04", title: "experiment-runbook.pdf", score: 0.91 },
  { id: "c-29", title: "operator-faq.md", score: 0.87 },
];

export default function App() {
  const [active, setActive] = useState(false);
  const [query, setQuery] = useState("How does Qwythlit assemble grounded context?");

  const particles = useMemo(
    () =>
      Array.from({ length: 22 }, (_, i) => ({
        id: i,
        top: 28 + ((i * 17) % 46),
        left: 38 + ((i * 23) % 48),
        delay: (i % 9) * -0.22,
        duration: 2.6 + (i % 5) * 0.36,
        size: 3 + (i % 3),
      })),
    []
  );

  return (
    <main className={`shell ${active ? "is-active" : ""}`}>
      <section className="hero">
        <div className="aurora aurora-a" />
        <div className="aurora aurora-b" />

        <header className="topbar">
          <div className="brand">
            <span className="brand-mark">Q</span>
            <div>
              <strong>Qwythlit</strong>
              <small>retrieval intelligence</small>
            </div>
          </div>

          <div className="status">
            <span className="status-dot" />
            context engine online
          </div>
        </header>

        <div className="copy">
          <p className="kicker">RAG / CAG VISUAL STUB</p>
          <h1>
            Ask once.
            <span>Watch context take flight.</span>
          </h1>
          <p className="lede">
            A dragon-shaped visualization for retrieval, reranking and synthesis.
            The artwork is static. The intelligence around it is not.
          </p>

          <div className="querybar">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Demo query"
            />
            <button onClick={() => setActive((v) => !v)}>
              <Flame size={18} />
              {active ? "Cool core" : "Ignite"}
            </button>
          </div>

          <div className="metrics">
            <span><Activity size={15} /> 12 ms router</span>
            <span><Database size={15} /> 3 chunks</span>
            <span><Sparkles size={15} /> grounded synthesis</span>
          </div>
        </div>

        <div className="visual" aria-label="Animated Qwythlit retrieval visualization">
          <div className="halo" />
          <div className="dragon-wrap">
            <img src="/qwythlit-dragon.jpg" alt="Rainbow spectral dragon" />
            <div className="dragon-sheen" />
          </div>

          <div className="breath">
            <div className="breath-core" />
            <div className="breath-tail" />
          </div>

          {particles.map((p) => (
            <i
              key={p.id}
              className="particle"
              style={{
                top: `${p.top}%`,
                left: `${p.left}%`,
                "--delay": `${p.delay}s`,
                "--duration": `${p.duration}s`,
                "--size": `${p.size}px`,
              }}
            />
          ))}

          {NODES.map(({ id, label, x, y, icon: Icon }) => (
            <button
              key={id}
              className="node"
              style={{ left: `${x}%`, top: `${y}%` }}
              title={label}
            >
              <Icon size={15} />
              <span>{label}</span>
            </button>
          ))}

          <svg className="graph" viewBox="0 0 100 100" preserveAspectRatio="none">
            <path d="M14 35 C 28 28, 34 46, 46 48" />
            <path d="M27 75 C 41 67, 46 55, 52 49" />
            <path d="M78 22 C 70 35, 66 42, 57 48" />
            <path d="M84 64 C 72 58, 66 53, 57 50" />
          </svg>

          <div className="core-readout">
            <small>CONTEXT CORE</small>
            <strong>{active ? "SYNTHESIZING" : "IDLE"}</strong>
            <span>{active ? "evidence lattice stable" : "awaiting query"}</span>
          </div>
        </div>
      </section>

      <section className="trace">
        <div className="trace-heading">
          <span>retrieval trace</span>
          <strong>{query}</strong>
        </div>

        <div className="chunk-list">
          {CHUNKS.map((chunk, index) => (
            <article
              className="chunk"
              key={chunk.id}
              style={{ "--i": index }}
            >
              <span className="chunk-rank">0{index + 1}</span>
              <div>
                <strong>{chunk.title}</strong>
                <small>{chunk.id} · cosine/rerank score</small>
              </div>
              <b>{chunk.score.toFixed(2)}</b>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
