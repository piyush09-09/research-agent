import { useNavigate, Link } from "react-router-dom";
import Logo from "../components/Logo";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing">
      <nav className="landing-nav">
        <div className="nav-left">
          <Logo size={26} />
          <span className="nav-brand">Research Agent</span>
        </div>
        <div className="nav-right">
          <button className="nav-link" onClick={() => navigate("/login")}>
            Log in
          </button>
          <button className="nav-cta" onClick={() => navigate("/login?mode=signup")}>
            Get Started
          </button>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-badge">Multi-Agent AI System</div>
        <h1 className="hero-title">
          Research any topic.<br />
          <span className="hero-highlight">Agents do the work.</span>
        </h1>
        <p className="hero-subtitle">
          Ask a question. Four AI agents plan, search the web, synthesize sources,
          and write a cited report — streamed to you in real time.
        </p>
        <div className="hero-actions">
          <button className="btn-primary" onClick={() => navigate("/login?mode=signup")}>
            Start Researching
          </button>
          <button className="btn-secondary" onClick={() => document.getElementById("how-it-works").scrollIntoView({ behavior: "smooth" })}>
            See How It Works
          </button>
        </div>
      </section>

      <section className="pipeline-visual">
        <div className="pipe-step">
          <div className="pipe-icon">01</div>
          <div className="pipe-label">Planner</div>
          <div className="pipe-desc">Breaks your query into focused sub-tasks</div>
        </div>
        <div className="pipe-connector" />
        <div className="pipe-step">
          <div className="pipe-icon">02</div>
          <div className="pipe-label">Researcher</div>
          <div className="pipe-desc">Searches the web and reads multiple sources</div>
        </div>
        <div className="pipe-connector" />
        <div className="pipe-step">
          <div className="pipe-icon">03</div>
          <div className="pipe-label">Synthesizer</div>
          <div className="pipe-desc">Finds the most relevant information via hybrid search</div>
        </div>
        <div className="pipe-connector" />
        <div className="pipe-step">
          <div className="pipe-icon">04</div>
          <div className="pipe-label">Writer</div>
          <div className="pipe-desc">Generates a cited report streamed in real time</div>
        </div>
      </section>

      <section className="features" id="how-it-works">
        <h2 className="section-title">What Happens Under the Hood</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-tag">Agentic</div>
            <h3>Tool Calling Loop</h3>
            <p>The LLM decides what to search and when to stop. Not a hardcoded chain — a real agent that reasons about its next action.</p>
          </div>
          <div className="feature-card">
            <div className="feature-tag">Real-time</div>
            <h3>SSE Streaming</h3>
            <p>Watch the report write itself token by token. Every agent step appears live in your browser via Server-Sent Events.</p>
          </div>
          <div className="feature-card">
            <div className="feature-tag">Retrieval</div>
            <h3>Hybrid RAG</h3>
            <p>Dense vector search + keyword matching in Qdrant. Cross-encoder re-ranking picks the truly relevant chunks.</p>
          </div>
          <div className="feature-card">
            <div className="feature-tag">Orchestration</div>
            <h3>LangGraph State Machine</h3>
            <p>Four agents share typed state through a directed graph. Parallel execution, automatic state merging, full observability.</p>
          </div>
        </div>
      </section>

      <section className="tech-strip">
        <span>LangGraph</span>
        <span>·</span>
        <span>Groq</span>
        <span>·</span>
        <span>Qdrant</span>
        <span>·</span>
        <span>FastAPI</span>
        <span>·</span>
        <span>React</span>
        <span>·</span>
        <span>SSE</span>
      </section>

      <section className="cta-section">
        <h2>Ready to try it?</h2>
        <p>No credit card. No setup. Just ask a research question.</p>
        <button className="btn-primary" onClick={() => navigate("/login?mode=signup")}>
          Create Free Account
        </button>
      </section>

      <footer className="landing-footer">
        <div className="footer-links">
          <Link to="/terms">Terms</Link>
          <span>·</span>
          <Link to="/privacy">Privacy</Link>
          <span>·</span>
          <a href="mailto:kpiyush0404@gmail.com">Contact</a>
        </div>
        <p>Built by Piyush Kumar · B.Tech CSE · IIIT Vadodara</p>
      </footer>
    </div>
  );
}