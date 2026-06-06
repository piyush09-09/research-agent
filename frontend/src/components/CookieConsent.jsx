import { useState, useEffect } from "react";

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem("cookies-accepted");
    if (!accepted) {
      const timer = setTimeout(() => setVisible(true), 1500);
      return () => clearTimeout(timer);
    }
  }, []);

  const accept = () => {
    localStorage.setItem("cookies-accepted", "true");
    setVisible(false);
  };

  const decline = () => {
    localStorage.setItem("cookies-accepted", "essential-only");
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="cookie-banner">
      <div className="cookie-text">
        <p>
          We use essential cookies to keep you logged in and optional cookies to
          improve your experience.{" "}
          <a href="/privacy" className="cookie-link">Privacy Policy</a>
        </p>
      </div>
      <div className="cookie-actions">
        <button className="cookie-decline" onClick={decline}>
          Essential Only
        </button>
        <button className="cookie-accept" onClick={accept}>
          Accept All
        </button>
      </div>
    </div>
  );
}