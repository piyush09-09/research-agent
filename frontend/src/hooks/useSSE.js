import { useState, useRef, useCallback } from "react";

export function useSSE() {
  const [tokens, setTokens] = useState("");
  const [steps, setSteps] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [evalScores, setEvalScores] = useState(null);
  const readerRef = useRef(null);

  const startResearch = useCallback(async (query, wordLimit = 500) => {
    setTokens("");
    setSteps([]);
    setTasks([]);
    setDone(false);
    setLoading(true);
    setError(false);
    setEvalScores(null);

    try {
      const token = localStorage.getItem("token");

      const response = await fetch("http://localhost:8000/research", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ query, word_limit: wordLimit }),
      });

      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "/login";
        return;
      }

      if (response.status === 429) {
        setError(true);
        setSteps(["Rate limit reached. Please wait before trying again."]);
        return;
      }

      const reader = response.body.getReader();
      readerRef.current = reader;
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done: streamDone, value } = await reader.read();
        if (streamDone) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const event = JSON.parse(line.slice(6));

            if (event.type === "step") {
              setSteps((prev) => [...prev, event.label]);
            } else if (event.type === "tasks") {
              setTasks(event.tasks);
            } else if (event.type === "token") {
              setTokens((prev) => prev + event.content);
            } else if (event.type === "eval") {
              setEvalScores(event.scores);
            } else if (event.type === "done") {
              setDone(true);
            }
          } catch (e) {
            // skip malformed
          }
        }
      }
    } catch (err) {
      console.error("SSE Error:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  return { tokens, steps, tasks, done, loading, error, evalScores, startResearch };
}