import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";
const STUDENT_ID = "STU001";

const exercises = [
  {
    id: 1,
    title: "Even or Odd",
    topic: "Conditional Statements",
    difficulty: "Beginner",
    description:
      "Write a Python program that determines whether an integer is even or odd.",
    input: "7",
    expectedOutput: "Odd",
    starterCode: `number = int(input("Enter a number: "))

# Write your code below
`,
    hint: "An even number is divisible by 2 with no remainder.",
    solution: `number = int(input("Enter a number: "))

if number % 2 == 0:
    print("Even")
else:
    print("Odd")`,
  },
  {
    id: 2,
    title: "Find the Largest Number",
    topic: "Conditional Statements",
    difficulty: "Beginner",
    description:
      "Write a program that accepts two numbers and prints the larger number.",
    input: "12\n8",
    expectedOutput: "12",
    starterCode: `a = int(input("Enter the first number: "))
b = int(input("Enter the second number: "))

# Write your code below
`,
    hint: "Compare the two numbers using an if-else statement.",
    solution: `a = int(input("Enter the first number: "))
b = int(input("Enter the second number: "))

if a > b:
    print(a)
elif b > a:
    print(b)
else:
    print("Both numbers are equal")`,
  },
  {
    id: 3,
    title: "Sum of Natural Numbers",
    topic: "Loops",
    difficulty: "Intermediate",
    description:
      "Calculate the sum of all natural numbers from 1 up to a number entered by the user.",
    input: "5",
    expectedOutput: "15",
    starterCode: `n = int(input("Enter a number: "))
total = 0

# Write your code below
`,
    hint: "Use a loop that visits each number from 1 through n and adds it to total.",
    solution: `n = int(input("Enter a number: "))
total = 0

for number in range(1, n + 1):
    total += number

print(total)`,
  },
];

function StatCard({ label, value, icon, detail }) {
  return (
    <article className="stat-card">
      <div className="stat-card-top">
        <span>{label}</span>
        <span className="stat-icon">{icon}</span>
      </div>
      <strong className="stat-value">{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function PageHeading({ eyebrow, title, description }) {
  return (
    <div className="page-heading">
      <span className="eyebrow">{eyebrow}</span>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activePage, setActivePage] = useState("Dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState("checking");

  const [selectedExercise, setSelectedExercise] = useState(exercises[0]);
  const [code, setCode] = useState(exercises[0].starterCode);

  const [helpLevel, setHelpLevel] = useState(0);
  const [showSolution, setShowSolution] = useState(false);

  const [notice, setNotice] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function loadData() {
    setLoading(true);

    try {
      const [healthResponse, dashboardResponse, attemptsResponse] =
        await Promise.all([
          fetch(`${API_URL}/health`),
          fetch(`${API_URL}/api/dashboard/${STUDENT_ID}`),
          fetch(
            `${API_URL}/api/attempts?student_id=${STUDENT_ID}&limit=50`
          ),
        ]);

      if (
        !healthResponse.ok ||
        !dashboardResponse.ok ||
        !attemptsResponse.ok
      ) {
        throw new Error("The backend could not load your learning records.");
      }

      const dashboardData = await dashboardResponse.json();
      const attemptsData = await attemptsResponse.json();

      setDashboard(dashboardData);

      // Support APIs that return either an array or an object containing items.
      setAttempts(
        Array.isArray(attemptsData)
          ? attemptsData
          : Array.isArray(attemptsData.items)
            ? attemptsData.items
            : []
      );

      setApiStatus("online");
    } catch (error) {
      console.error("CodeHabit API error:", error);
      setApiStatus("offline");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function navigate(page) {
    setActivePage(page);
    setNotice("");
  }

  function chooseExercise(exercise) {
    setSelectedExercise(exercise);
    setCode(exercise.starterCode);
    setHelpLevel(0);
    setShowSolution(false);
    setPrediction(null);
    setNotice("");
    setActivePage("Practice");
  }

  function resetCode() {
    setCode(selectedExercise.starterCode);
    setNotice("");
    setPrediction(null);
    setHelpLevel(0);
    setShowSolution(false);
  }

  async function submitCode() {
    if (!code.trim()) {
      setNotice("Please write some code before submitting your attempt.");
      return;
    }

    if (apiStatus !== "online") {
      setNotice(
        "The backend is disconnected. Start your FastAPI server and try again."
      );
      return;
    }

    setSubmitting(true);
    setNotice("");
    setPrediction(null);

    try {
      const payload = {
        student_id: STUDENT_ID,
        topic: selectedExercise.topic,
        attempt_number: attempts.length + 1,
        previous_errors: attempts.filter(
          (item) => !item.is_correct
        ).length,
        syntax_error: 0,
        test_pass_rate: 0,
        execution_time: 0,
        is_correct: false,
      };

      const response = await fetch(`${API_URL}/api/attempts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail || "The attempt could not be saved."
        );
      }

      setPrediction({
        predicted_error: result.predicted_error || "Prediction unavailable",
        recommendation:
          "Review the exercise requirements, examine your logic, and try again.",
      });

      setNotice(
        "Your attempt information was saved. Automatic Python execution and correctness checking are not implemented yet."
      );

      await loadData();
    } catch (error) {
      setNotice(`Unable to submit your attempt: ${error.message}`);
    } finally {
      setSubmitting(false);
    }
  }

  function renderDashboard() {
    const total = dashboard?.total_attempts ?? attempts.length;
    const correct = dashboard?.correct_attempts ?? 0;
    const accuracy = dashboard?.accuracy_percentage ?? 0;

    return (
      <>
        <section className="welcome-banner">
          <div>
            <span className="eyebrow">YOUR LEARNING WORKSPACE</span>
            <h2>Small steps. Stronger coding skills.</h2>
            <p>
              Practise programming, understand your mistakes, and build
              confidence one exercise at a time.
            </p>
            <button
              className="primary-button"
              onClick={() => navigate("Exercises")}
            >
              Start practising →
            </button>
          </div>

          <div className="welcome-art" aria-hidden="true">
            <div className="art-window">
              <div className="art-dots">
                <i />
                <i />
                <i />
              </div>
              <div className="art-code">
                <span>01</span> <b>learn</b>() <br />
                <span>02</span> &nbsp; practise() <br />
                <span>03</span> &nbsp; improve()
              </div>
              <div className="art-check">✓</div>
            </div>
          </div>
        </section>

        <div className="section-heading">
          <div>
            <span className="eyebrow">YOUR OVERVIEW</span>
            <h2>Learning statistics</h2>
          </div>

          <span className={`status-pill ${apiStatus}`}>
            <i />
            {apiStatus === "online"
              ? "Backend connected"
              : apiStatus === "offline"
                ? "Backend disconnected"
                : "Connecting..."}
          </span>
        </div>

        <section className="stats-grid">
          <StatCard
            label="Total attempts"
            value={loading ? "…" : total}
            icon="⌘"
            detail="Recorded attempts"
          />
          <StatCard
            label="Correct attempts"
            value={loading ? "…" : correct}
            icon="✓"
            detail="Marked as correct"
          />
          <StatCard
            label="Accuracy"
            value={loading ? "…" : `${accuracy}%`}
            icon="◉"
            detail="Based on saved records"
          />
          <StatCard
            label="Exercises"
            value={exercises.length}
            icon="▤"
            detail="Available to practise"
          />
        </section>

        <div className="content-grid">
          <section className="panel progress-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">KEEP GOING</span>
                <h3>Your progress</h3>
              </div>
              <span className="panel-icon">↗</span>
            </div>

            <div
              className="progress-circle"
              style={{ "--progress": `${accuracy}%` }}
            >
              <div>
                <strong>{accuracy}%</strong>
                <span>accuracy</span>
              </div>
            </div>

            <p className="muted-text">
              {total === 0
                ? "Your journey starts with your first practice attempt."
                : `You have recorded ${total} attempt${total === 1 ? "" : "s"}. Keep practising to build consistency.`}
            </p>
          </section>

          <section className="panel quick-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">PICK UP WHERE YOU LEFT OFF</span>
                <h3>Quick practice</h3>
              </div>
              <span className="panel-icon">⌁</span>
            </div>

            {exercises.map((exercise) => (
              <button
                className="quick-exercise"
                key={exercise.id}
                onClick={() => chooseExercise(exercise)}
              >
                <span className="exercise-symbol">&lt;/&gt;</span>
                <span className="quick-exercise-text">
                  <strong>{exercise.title}</strong>
                  <small>{exercise.topic}</small>
                </span>
                <span className="arrow">→</span>
              </button>
            ))}
          </section>
        </div>

        <section className="panel recent-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">YOUR ACTIVITY</span>
              <h3>Recent attempts</h3>
            </div>

            <button
              className="text-button"
              onClick={() => navigate("History")}
            >
              View all →
            </button>
          </div>

          {attempts.length === 0 ? (
            <div className="empty-state">
              <span>⌁</span>
              <strong>No attempts yet</strong>
              <p>Start practising to build your learning history.</p>
            </div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Topic</th>
                    <th>Attempt</th>
                    <th>Predicted category</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {attempts.slice(0, 5).map((item) => (
                    <tr key={item.id}>
                      <td>{item.topic}</td>
                      <td>#{item.attempt_number}</td>
                      <td>{item.predicted_error || "Not available"}</td>
                      <td>
                        <span
                          className={`result-pill ${item.is_correct ? "success" : "pending"}`}
                        >
                          {item.is_correct ? "Correct" : "Needs review"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </>
    );
  }

  function renderExercises() {
    return (
      <>
        <PageHeading
          eyebrow="BUILD YOUR SKILLS"
          title="Practice exercises"
          description="Choose a task, think through the problem, and write your own solution."
        />

        <div className="exercise-grid">
          {exercises.map((exercise, index) => (
            <article className="exercise-card" key={exercise.id}>
              <div className="exercise-card-top">
                <span className="exercise-symbol">&lt;/&gt;</span>
                <span className="difficulty">{exercise.difficulty}</span>
              </div>

              <span className="eyebrow">
                EXERCISE {String(index + 1).padStart(2, "0")}
              </span>

              <h3>{exercise.title}</h3>
              <p>{exercise.description}</p>

              <div className="exercise-card-footer">
                <span>{exercise.topic}</span>
                <button
                  className="primary-button small"
                  onClick={() => chooseExercise(exercise)}
                >
                  Start exercise →
                </button>
              </div>
            </article>
          ))}
        </div>
      </>
    );
  }

  function renderPractice() {
    return (
      <>
        <PageHeading
          eyebrow="PRACTICE MODE"
          title={selectedExercise.title}
          description={selectedExercise.description}
        />

        <div className="practice-layout">
          <section className="panel exercise-instructions">
            <span className="eyebrow">TASK DETAILS</span>
            <h3>Your challenge</h3>
            <p>{selectedExercise.description}</p>

            <div className="example-box">
              <span>EXAMPLE INPUT</span>
              <pre>{selectedExercise.input}</pre>
            </div>

            <div className="example-box">
              <span>EXPECTED OUTPUT</span>
              <pre>{selectedExercise.expectedOutput}</pre>
            </div>

            <div className="notice-box">
              Try solving the exercise yourself before revealing the solution.
            </div>

            <button
              className="secondary-button full-button"
              onClick={() => navigate("Code Help")}
            >
              I'm stuck — help me
            </button>
          </section>

          <section className="panel editor-panel">
            <div className="editor-toolbar">
              <span>
                <i /> main.py
              </span>
              <span>Python 3</span>
            </div>

            <label className="editor-label" htmlFor="code-editor">
              YOUR CODE
            </label>

            <textarea
              id="code-editor"
              className="code-editor"
              spellCheck="false"
              value={code}
              onChange={(event) => setCode(event.target.value)}
              placeholder="Write your Python code here..."
            />

            <div className="editor-actions">
              <button className="secondary-button" onClick={resetCode}>
                Reset code
              </button>

              <button
                className="primary-button"
                disabled={submitting}
                onClick={submitCode}
              >
                {submitting ? "Submitting..." : "Submit attempt →"}
              </button>
            </div>

            <p className="muted-text small-note">
              Note: this version saves attempt information but does not
              execute or automatically test your Python code.
            </p>

            {notice && <div className="notice-box">{notice}</div>}

            {prediction && (
              <div className="prediction-box">
                <span className="eyebrow">EXPERIMENTAL ML PREDICTION</span>
                <h3>{prediction.predicted_error}</h3>
                <p>{prediction.recommendation}</p>
                <small>
                  This prediction uses attempt metadata. It does not analyse
                  or diagnose your actual source code.
                </small>
              </div>
            )}
          </section>
        </div>
      </>
    );
  }

  function renderCodeHelp() {
    const hints = [
      selectedExercise.hint,
      `Input: ${selectedExercise.input}. Identify the information your program receives and the result it must produce.`,
      `Expected output: ${selectedExercise.expectedOutput}. Think about which condition, calculation, or loop will produce that result.`,
    ];

    function revealNextHint() {
      setHelpLevel((current) => Math.min(current + 1, hints.length));
    }

    return (
      <>
        <PageHeading
          eyebrow="LEARN WITHOUT GIVING UP"
          title="Code Help"
          description="Get hints step by step. If you are still stuck, reveal an example solution and learn how it works."
        />

        <div className="help-layout">
          <section className="panel help-exercise">
            <span className="eyebrow">CURRENT EXERCISE</span>
            <h3>{selectedExercise.title}</h3>
            <p>{selectedExercise.description}</p>

            <div className="example-box">
              <span>EXAMPLE INPUT</span>
              <pre>{selectedExercise.input}</pre>
            </div>

            <div className="example-box">
              <span>EXPECTED OUTPUT</span>
              <pre>{selectedExercise.expectedOutput}</pre>
            </div>

            <button
              className="secondary-button full-button"
              onClick={() => navigate("Practice")}
            >
              ← Back to editor
            </button>
          </section>

          <section className="panel help-content">
            <span className="eyebrow">YOUR LEARNING GUIDE</span>
            <h3>Let's solve it together</h3>

            <p>
              Try each hint before moving to the next one. Understanding the
              logic is more important than memorising the answer.
            </p>

            {hints.slice(0, helpLevel).map((hint, index) => (
              <div className="hint-card" key={index}>
                <span className="eyebrow">HINT {index + 1}</span>
                <p>{hint}</p>
              </div>
            ))}

            {helpLevel < hints.length && (
              <button
                className="primary-button"
                onClick={revealNextHint}
              >
                Show next hint →
              </button>
            )}

            {helpLevel >= hints.length && !showSolution && (
              <p className="muted-text">
                You have seen all the hints. If you still need help, you can
                reveal the example solution.
              </p>
            )}

            {!showSolution && (
              <button
                className="secondary-button full-button"
                onClick={() => setShowSolution(true)}
              >
                Show complete example solution
              </button>
            )}

            {showSolution && (
              <div className="solution-card">
                <span className="eyebrow">EXAMPLE SOLUTION</span>
                <pre>{selectedExercise.solution}</pre>

                <p>
                  Read each line and make sure you understand why it is
                  needed. Then return to the editor and try writing the
                  solution yourself.
                </p>

                <button
                  className="primary-button"
                  onClick={() => {
                    setCode(selectedExercise.solution);
                    setActivePage("Practice");
                    setNotice(
                      "Example solution loaded into the editor. Study it and modify it to understand how it works."
                    );
                  }}
                >
                  Load solution into editor →
                </button>
              </div>
            )}
          </section>
        </div>
      </>
    );
  }

  function renderHistory() {
    return (
      <>
        <PageHeading
          eyebrow="YOUR LEARNING JOURNEY"
          title="Attempt history"
          description="Review your saved attempts and see which topics you have practised."
        />

        <section className="panel recent-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">SAVED RECORDS</span>
              <h3>All attempts</h3>
            </div>

            <button
              className="secondary-button"
              onClick={loadData}
              disabled={loading}
            >
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>

          {attempts.length === 0 ? (
            <div className="empty-state">
              <span>⌁</span>
              <strong>No saved attempts</strong>
              <p>Your attempts will appear here after you submit them.</p>
            </div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Topic</th>
                    <th>Attempt</th>
                    <th>Predicted category</th>
                    <th>Result</th>
                  </tr>
                </thead>

                <tbody>
                  {attempts.map((item) => (
                    <tr key={item.id}>
                      <td>{item.topic}</td>
                      <td>#{item.attempt_number}</td>
                      <td>{item.predicted_error || "Not available"}</td>
                      <td>
                        <span
                          className={`result-pill ${item.is_correct ? "success" : "pending"}`}
                        >
                          {item.is_correct ? "Correct" : "Needs review"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </>
    );
  }

  const navItems = [
    { name: "Dashboard", icon: "⌂" },
    { name: "Exercises", icon: "▤" },
    { name: "Practice", icon: "</>" },
    { name: "Code Help", icon: "✳" },
    { name: "History", icon: "◷" },
  ];

  function renderPage() {
    switch (activePage) {
      case "Dashboard":
        return renderDashboard();

      case "Exercises":
        return renderExercises();

      case "Practice":
        return renderPractice();

      case "Code Help":
        return renderCodeHelp();

      case "History":
        return renderHistory();

      default:
        return renderDashboard();
    }
  }

  return (
    <div className="app-shell">
    <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>
        <button
          className="sidebar-close"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close sidebar"
          type="button"
        >
        ☰
        </button>
        <div className="brand">
          <div className="brand-mark">&lt;/&gt;</div>
          <div>
            <h1>CodeHabit</h1>
            <span>LEARN · PRACTISE · GROW</span>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${activePage === item.name ? "active" : ""}`}
              onClick={() => navigate(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.name}</span>

              {item.name === "Code Help" && (
                <span className="nav-badge">HELP</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="connection-indicator">
            <span className={`connection-dot ${apiStatus}`} />
            <div>
              <strong>
                {apiStatus === "online"
                  ? "API connected"
                  : apiStatus === "offline"
                    ? "API offline"
                    : "Connecting"}
              </strong>
              <small>CodeHabit backend</small>
            </div>
          </div>

          <div className="student-profile">
            <div className="avatar">S</div>
            <div>
              <strong>Student</strong>
              <small>Learning account</small>
            </div>
          </div>
        </div>
      </aside>

      <main
  className={`main-content ${
    sidebarOpen ? "sidebar-visible" : "sidebar-hidden"
  }`}
>
  {!sidebarOpen && (
    <button
      className="sidebar-open-button"
      onClick={() => setSidebarOpen(true)}
      type="button"
      aria-label="Open sidebar"
      title="Open sidebar"
    >
      ☰
    </button>
  )}  <header className="topbar">
          <div className="breadcrumb">
            <span>CodeHabit</span>
            <span>/</span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <span className={`status-pill ${apiStatus}`}>
              <i />
              {apiStatus === "online"
                ? "Connected"
                : apiStatus === "offline"
                  ? "Offline"
                  : "Connecting"}
            </span>

            <button
              className="refresh-button"
              onClick={loadData}
              disabled={loading}
              title="Refresh dashboard data"
              aria-label="Refresh dashboard data"
            >
              ↻
            </button>
          </div>
        </header>

        <div className="page-content">{renderPage()}</div>

        <footer className="app-footer">
          <span>CodeHabit</span>
          <span>Build consistency, one line at a time.</span>
        </footer>
      </main>
    </div>
  );
}

export default App;

