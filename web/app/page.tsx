"use client";

import { useEffect, useRef, useState } from "react";
import styles from "./page.module.css";

type Source = { source: string; page: number | null; score: number };
type Message = { role: "user" | "ai"; text: string; sources?: Source[] };

const API_URL = "http://localhost:8000/ask_query";

// apni handbook ke asli sawal yahan daalo
const SUGGESTIONS = [
  "What is the return policy?",
  "What are the shop opening hours?",
  "How do I handle a customer complaint?",
  "What is the dress code?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [asked, setAsked] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function newChat() {
    if (loading) return;
    setMessages([]);
    setInput("");
  }

  async function send(text?: string) {
    const question = (text ?? input).trim();
    if (!question || loading) return;

    setMessages((m) => [...m, { role: "user", text: question }]);
    setAsked((a) => (a.includes(question) ? a : [question, ...a].slice(0, 8)));
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: "ai", text: data.answer, sources: data.sources },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "ai", text: "Something went wrong. Is the API running?" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <div className={styles.logo}>C</div>
          <div>
            <div className={styles.title}>Clause</div>
            <div className={styles.subtitle}>Shop Assistant</div>
          </div>
        </div>

        <button className={styles.newChat} onClick={newChat}>
          + New chat
        </button>

        {asked.length > 0 && (
          <>
            <div className={styles.sectionLabel}>Recent</div>
            <div className={styles.list}>
              {asked.map((q) => (
                <button key={q} className={styles.item} onClick={() => send(q)}>
                  {q}
                </button>
              ))}
            </div>
          </>
        )}

        <div className={styles.sideFooter}>Answers come only from the shop handbook.</div>
      </aside>

      <section className={styles.main}>
        <header className={styles.topbar}>
          <div className={styles.topTitle}>Ask the handbook</div>
          <div className={styles.status}>
            <span className={styles.dot} /> Online
          </div>
        </header>

        <div className={styles.chat}>
          <div className={styles.chatInner}>
            {messages.length === 0 && (
              <div className={styles.empty}>
                <div className={styles.bigLogo}>C</div>
                <h2>How can I help today?</h2>
                <p>Ask about policies, procedures or anything in the Clause shop handbook.</p>
                <div className={styles.cards}>
                  {SUGGESTIONS.map((s) => (
                    <button key={s} className={styles.card} onClick={() => send(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((m, i) => (
              <div
                key={i}
                className={`${styles.row} ${m.role === "user" ? styles.rowUser : ""}`}
              >
                <div className={`${styles.avatar} ${m.role === "user" ? styles.avatarUser : ""}`}>
                  {m.role === "user" ? "U" : "C"}
                </div>
                <div className={styles.msgCol}>
                  <div
                    className={`${styles.bubble} ${
                      m.role === "user" ? styles.user : styles.ai
                    }`}
                  >
                    {m.text}
                  </div>
                  {m.sources && m.sources.length > 0 && (
                    <div className={styles.sources}>
                      {Array.from(
                        new Set(
                          m.sources.map(
                            (s) =>
                              `${s.source.split(/[\\/]/).pop()}${
                                s.page !== null ? ` · page ${s.page + 1}` : ""
                              }`
                          )
                        )
                      ).map((label) => (
                        <span key={label} className={styles.source}>
                          {label}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className={styles.row}>
                <div className={styles.avatar}>C</div>
                <div className={styles.msgCol}>
                  <div className={`${styles.bubble} ${styles.ai}`}>
                    <span className={styles.dots}>
                      <span />
                      <span />
                      <span />
                    </span>
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <footer className={styles.footer}>
          <div className={styles.inputWrap}>
            <input
              className={styles.input}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Ask something about the handbook..."
            />
            <button
              className={styles.send}
              onClick={() => send()}
              disabled={loading || !input.trim()}
            >
              Send
            </button>
          </div>
        </footer>
      </section>
    </div>
  );
}