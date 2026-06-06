import { useNavigate } from "react-router-dom";
import Logo from "../components/Logo";

export default function Privacy() {
  const navigate = useNavigate();

  return (
    <div className="legal-page">
      <nav className="legal-nav">
        <div className="nav-left" onClick={() => navigate("/")} style={{ cursor: "pointer" }}>
          <Logo size={26} />
          <span className="nav-brand">Research Agent</span>
        </div>
      </nav>

      <article className="legal-content">
        <h1>Privacy Policy</h1>
        <p className="legal-updated">Last updated: June 2026</p>

        <h2>1. Information We Collect</h2>
        <p>When you use Research Agent, we collect:</p>
        <ul>
          <li><strong>Account information:</strong> Name, email address, and hashed password when you create an account</li>
          <li><strong>Research queries:</strong> The questions you submit for research</li>
          <li><strong>Generated reports:</strong> Reports produced by the AI agents</li>
          <li><strong>Usage data:</strong> Basic interaction data such as timestamps and feature usage</li>
        </ul>

        <h2>2. How We Use Your Information</h2>
        <ul>
          <li>To provide and maintain the Service</li>
          <li>To authenticate your identity</li>
          <li>To store your research history for your convenience</li>
          <li>To improve the quality of AI-generated reports</li>
        </ul>

        <h2>3. Third-Party Services</h2>
        <p>The Service uses the following third-party providers:</p>
        <ul>
          <li><strong>Groq:</strong> LLM inference for AI agents</li>
          <li><strong>DuckDuckGo:</strong> Web search (no personal data sent)</li>
          <li><strong>Qdrant:</strong> Vector database for document storage</li>
        </ul>
        <p>
          Your research queries are sent to Groq's API for processing. We
          recommend reviewing Groq's privacy policy for details on their data
          handling practices.
        </p>

        <h2>4. Data Storage and Security</h2>
        <p>
          Your data is stored securely. Passwords are hashed and never stored in
          plain text. We implement reasonable security measures to protect your
          information, but no method of transmission over the internet is 100%
          secure.
        </p>

        <h2>5. Cookies</h2>
        <p>We use the following cookies:</p>
        <ul>
          <li><strong>Essential cookies:</strong> Authentication tokens stored in localStorage to keep you logged in</li>
          <li><strong>Preference cookies:</strong> Your cookie consent choice and UI preferences</li>
        </ul>
        <p>We do not use tracking cookies, advertising cookies, or analytics cookies.</p>

        <h2>6. Your Rights</h2>
        <p>You have the right to:</p>
        <ul>
          <li>Access your personal data</li>
          <li>Request deletion of your account and associated data</li>
          <li>Export your research history</li>
          <li>Withdraw consent for optional cookies at any time</li>
        </ul>

        <h2>7. Data Retention</h2>
        <p>
          We retain your data for as long as your account is active. If you
          delete your account, all associated data is permanently removed within
          30 days.
        </p>

        <h2>8. Children's Privacy</h2>
        <p>
          The Service is not intended for users under 13 years of age. We do not
          knowingly collect personal information from children.
        </p>

        <h2>9. Contact</h2>
        <p>
          For privacy-related questions or data requests, contact us at{" "}
          <a href="mailto:kpiyush0404@gmail.com">kpiyush0404@gmail.com</a>.
        </p>
      </article>
    </div>
  );
}