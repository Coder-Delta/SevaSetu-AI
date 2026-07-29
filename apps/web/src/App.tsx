import { FormEvent, useEffect, useMemo, useState } from "react";

type LanguageCode = "en" | "hi" | "bn";

type TokenResponse = {
  access_token: string;
  token_type: string;
};

type UserProfile = {
  id: string;
  email: string;
  full_name: string | null;
  preferred_language: LanguageCode;
  input_mode: string;
  age: number | null;
  income_bracket: string | null;
  category: string | null;
  occupation: string | null;
  location_state: string | null;
  location_district: string | null;
  education_level: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

type Scheme = {
  id: string;
  scheme_name: string;
  slug: string;
  details: string | null;
  benefits: string | null;
  eligibility: string | null;
  application_process: string | null;
  documents_required: string | null;
  level: string | null;
  scheme_category: string | null;
  tags: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

type SchemeSearchResult = {
  scheme: Scheme;
  relevance_score: number;
  eligibility_explanation: string | null;
};

type Application = {
  id: string;
  user_id: string;
  scheme_id: string;
  status: string;
  documents_metadata: Record<string, string> | null;
  eligibility_score: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  scheme: Scheme | null;
};

type ChatResponse = {
  response: string;
  language: string;
  conversation_id: string;
  schemes_referenced?: Scheme[];
};

type ApiError = {
  detail?: string;
};

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://127.0.0.1:8000";
const TOKEN_STORAGE_KEY = "sevasetu-access-token";

const languageOptions: { value: LanguageCode; label: string; hint: string }[] = [
  { value: "en", label: "English", hint: "Simple UI copy" },
  { value: "hi", label: "Hindi", hint: "Citizen guidance in Hindi" },
  { value: "bn", label: "Bengali", hint: "Citizen guidance in Bengali" },
];

const emptyProfileForm = {
  full_name: "",
  preferred_language: "en" as LanguageCode,
  input_mode: "text",
  age: "",
  income_bracket: "",
  category: "",
  occupation: "",
  location_state: "",
  location_district: "",
  education_level: "",
};

function App() {
  const [token, setToken] = useState<string>(() => window.localStorage.getItem(TOKEN_STORAGE_KEY) ?? "");
  const [registerForm, setRegisterForm] = useState({
    email: "",
    password: "",
    full_name: "",
    preferred_language: "en" as LanguageCode,
    input_mode: "text",
  });
  const [loginForm, setLoginForm] = useState({
    email: "",
    password: "",
  });
  const [profileForm, setProfileForm] = useState(emptyProfileForm);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [schemeQuery, setSchemeQuery] = useState("women scholarship");
  const [schemeResults, setSchemeResults] = useState<SchemeSearchResult[]>([]);
  const [chatMessage, setChatMessage] = useState("Please suggest schemes I may qualify for.");
  const [chatHistory, setChatHistory] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [activeSchemeId, setActiveSchemeId] = useState<string>("");
  const [statusMessage, setStatusMessage] = useState("Connect your profile to start guided discovery.");
  const [loadingKey, setLoadingKey] = useState<string | null>(null);

  const selectedLanguage = profileForm.preferred_language;
  const canUseProtectedFeatures = Boolean(token);

  const schemeCards = useMemo(() => {
    return schemeResults.map((result) => ({
      ...result,
      shortDetails: truncateText(result.scheme.details),
      shortBenefits: truncateText(result.scheme.benefits),
      shortEligibility: truncateText(result.scheme.eligibility),
    }));
  }, [schemeResults]);

  useEffect(() => {
    if (!token) {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
      setProfile(null);
      setApplications([]);
      setChatHistory([]);
      setConversationId(null);
      setProfileForm(emptyProfileForm);
      return;
    }

    window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
    void loadProfile(token);
    void loadApplications(token);
  }, [token]);

  async function apiRequest<T>(path: string, options: RequestInit = {}, accessToken = token): Promise<T> {
    const headers = new Headers(options.headers ?? {});
    headers.set("Content-Type", "application/json");
    if (accessToken) {
      headers.set("Authorization", `Bearer ${accessToken}`);
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorBody = (await response.json().catch(() => ({}))) as ApiError;
      throw new Error(errorBody.detail ?? `Request failed with status ${response.status}`);
    }

    return (await response.json()) as T;
  }

  async function loadProfile(accessToken = token) {
    if (!accessToken) {
      return;
    }

    try {
      const nextProfile = await apiRequest<UserProfile>("/api/v1/profile/me", { method: "GET" }, accessToken);
      setProfile(nextProfile);
      setProfileForm({
        full_name: nextProfile.full_name ?? "",
        preferred_language: nextProfile.preferred_language,
        input_mode: nextProfile.input_mode,
        age: nextProfile.age?.toString() ?? "",
        income_bracket: nextProfile.income_bracket ?? "",
        category: nextProfile.category ?? "",
        occupation: nextProfile.occupation ?? "",
        location_state: nextProfile.location_state ?? "",
        location_district: nextProfile.location_district ?? "",
        education_level: nextProfile.education_level ?? "",
      });
      setStatusMessage(`Welcome back, ${nextProfile.full_name ?? nextProfile.email}.`);
    } catch (error) {
      setStatusMessage(getErrorMessage(error));
    }
  }

  async function loadApplications(accessToken = token) {
    if (!accessToken) {
      return;
    }

    try {
      const nextApplications = await apiRequest<Application[]>("/api/v1/applications/me", { method: "GET" }, accessToken);
      setApplications(nextApplications);
    } catch (error) {
      setStatusMessage(getErrorMessage(error));
    }
  }

  async function handleRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingKey("register");
    try {
      await apiRequest<UserProfile>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify(registerForm),
      }, "");
      setStatusMessage("Account created. Sign in to continue.");
      setLoginForm({
        email: registerForm.email,
        password: registerForm.password,
      });
    } catch (error) {
      setStatusMessage(getErrorMessage(error));
    } finally {
      setLoadingKey(null);
    }
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingKey("login");
    try {
      const response = await apiRequest<TokenResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify(loginForm),
      }, "");
      setToken(response.access_token);
      setStatusMessage("Session unlocked. Complete your profile to improve scheme matching.");
    } catch (error) {
      setStatusMessage(getErrorMessage(error));
    } finally {
      setLoadingKey(null);
    }
  }

  async function handleProfileSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingKey("profile");
    try {
      const payload = {
        ...profileForm,
        age: profileForm.age ? Number(profileForm.age) : null,
      };
      const nextProfile = await apiRequest<UserProfile>("/api/v1/profile/me", {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      setProfile(nextProfile);
      setStatusMessage("Profile updated. Your scheme checks will now use the latest details.");
    } catch (error) {
      setStatusMessage(getErrorMessage(error));
    } finally {
      setLoadingKey(null);
    }
  }

  async function handleSchemeSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingKey("search");
    try {
      const results = await apiRequest<SchemeSearchResult[]>("/api/v1/schemes/search", {
        method: "POST",
        body: JSON.stringify({
          query: schemeQuery,
          language: selectedLanguage,
          top_k: 5,
        }),
      });
      setSchemeResults(results);
      if (results[0]) {
        setActiveSchemeId(results[0].scheme.id);
      }
      setStatusMessage(`Found ${results.length} scheme matches.`);
    } catch (error) {
      setStatusMessage(getErrorMessage(error));
    } finally {
      setLoadingKey(null);
    }
  }

  async function handleChat(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!chatMessage.trim()) {
      return;
    }

    setLoadingKey("chat");
    const nextHistory = [...chatHistory, { role: "user" as const, content: chatMessage }];
    setChatHistory(nextHistory);
    try {
      const response = await apiRequest<ChatResponse>("/api/v1/chat/", {
        method: "POST",
        body: JSON.stringify({
          message: chatMessage,
          language: selectedLanguage,
          conversation_id: conversationId,
        }),
      });
      setConversationId(response.conversation_id);
      setChatHistory([...nextHistory, { role: "assistant", content: response.response }]);
      setChatMessage("");
      setStatusMessage("Assistant response generated.");
    } catch (error) {
      setChatHistory(chatHistory);
      setStatusMessage(getErrorMessage(error));
    } finally {
      setLoadingKey(null);
    }
  }

  async function handleCreateApplication(schemeId: string) {
    setLoadingKey(`application-${schemeId}`);
    try {
      await apiRequest<Application>("/api/v1/applications/", {
        method: "POST",
        body: JSON.stringify({
          scheme_id: schemeId,
        }),
      });
      await loadApplications();
      setStatusMessage("Application draft created.");
    } catch (error) {
      setStatusMessage(getErrorMessage(error));
    } finally {
      setLoadingKey(null);
    }
  }

  function logout() {
    setToken("");
    setStatusMessage("Signed out. The dashboard is back in preview mode.");
  }

  return (
    <div className="page-shell">
      <div className="ambient ambient-left" />
      <div className="ambient ambient-right" />

      <header className="hero">
        <div className="hero-copy">
          <span className="eyebrow">SevaSetu AI</span>
          <h1>One civic workspace for welfare discovery, guidance, and action.</h1>
          <p>
            Move from scheme confusion to a clear next step. The interface below is wired to your FastAPI backend
            and supports English, Hindi, and Bengali flows.
          </p>
          <div className="hero-badges">
            <span>Phase 1 mock data</span>
            <span>Profile-aware eligibility</span>
            <span>Draft application workflow</span>
          </div>
        </div>
      </header>

      <main className="dashboard-grid">
        <section className="panel auth-panel">
          <div className="panel-heading">
            <span className="panel-kicker">1. Onboarding</span>
            <h2>Start with access</h2>
          </div>

          <div className="auth-columns">
            <form className="stack-form" onSubmit={handleRegister}>
              <h3>Create account</h3>
              <label>
                Full name
                <input
                  value={registerForm.full_name}
                  onChange={(event) => setRegisterForm({ ...registerForm, full_name: event.target.value })}
                  placeholder="Asha Verma"
                  required
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  value={registerForm.email}
                  onChange={(event) => setRegisterForm({ ...registerForm, email: event.target.value })}
                  placeholder="asha@example.com"
                  required
                />
              </label>
              <label>
                Password
                <input
                  type="password"
                  value={registerForm.password}
                  onChange={(event) => setRegisterForm({ ...registerForm, password: event.target.value })}
                  placeholder="Create a password"
                  required
                />
              </label>
              <label>
                Preferred language
                <select
                  value={registerForm.preferred_language}
                  onChange={(event) =>
                    setRegisterForm({
                      ...registerForm,
                      preferred_language: event.target.value as LanguageCode,
                    })
                  }
                >
                  {languageOptions.map((language) => (
                    <option key={language.value} value={language.value}>
                      {language.label}
                    </option>
                  ))}
                </select>
              </label>
              <button className="primary-button" type="submit" disabled={loadingKey === "register"}>
                {loadingKey === "register" ? "Creating..." : "Create citizen account"}
              </button>
            </form>

            <form className="stack-form" onSubmit={handleLogin}>
              <h3>Return to dashboard</h3>
              <label>
                Email
                <input
                  type="email"
                  value={loginForm.email}
                  onChange={(event) => setLoginForm({ ...loginForm, email: event.target.value })}
                  placeholder="asha@example.com"
                  required
                />
              </label>
              <label>
                Password
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })}
                  placeholder="Your password"
                  required
                />
              </label>
              <button className="secondary-button" type="submit" disabled={loadingKey === "login"}>
                {loadingKey === "login" ? "Signing in..." : "Sign in"}
              </button>
            </form>
          </div>
        </section>

        <section className="panel profile-panel">
          <div className="panel-heading">
            <span className="panel-kicker">2. Profile Capture</span>
            <h2>Tell SevaSetu who you are</h2>
          </div>
          <form className="profile-grid" onSubmit={handleProfileSave}>
            <label>
              Full name
              <input
                value={profileForm.full_name}
                onChange={(event) => setProfileForm({ ...profileForm, full_name: event.target.value })}
                placeholder="Citizen name"
              />
            </label>
            <label>
              Age
              <input
                type="number"
                min="0"
                value={profileForm.age}
                onChange={(event) => setProfileForm({ ...profileForm, age: event.target.value })}
                placeholder="28"
              />
            </label>
            <label>
              Annual income
              <input
                value={profileForm.income_bracket}
                onChange={(event) => setProfileForm({ ...profileForm, income_bracket: event.target.value })}
                placeholder="250000"
              />
            </label>
            <label>
              Category
              <input
                value={profileForm.category}
                onChange={(event) => setProfileForm({ ...profileForm, category: event.target.value })}
                placeholder="SC / ST / OBC / General"
              />
            </label>
            <label>
              Occupation
              <input
                value={profileForm.occupation}
                onChange={(event) => setProfileForm({ ...profileForm, occupation: event.target.value })}
                placeholder="Student, farmer, worker..."
              />
            </label>
            <label>
              Education level
              <input
                value={profileForm.education_level}
                onChange={(event) => setProfileForm({ ...profileForm, education_level: event.target.value })}
                placeholder="12th pass"
              />
            </label>
            <label>
              State
              <input
                value={profileForm.location_state}
                onChange={(event) => setProfileForm({ ...profileForm, location_state: event.target.value })}
                placeholder="West Bengal"
              />
            </label>
            <label>
              District
              <input
                value={profileForm.location_district}
                onChange={(event) => setProfileForm({ ...profileForm, location_district: event.target.value })}
                placeholder="Kolkata"
              />
            </label>
            <label>
              Language
              <select
                value={profileForm.preferred_language}
                onChange={(event) =>
                  setProfileForm({
                    ...profileForm,
                    preferred_language: event.target.value as LanguageCode,
                  })
                }
              >
                {languageOptions.map((language) => (
                  <option key={language.value} value={language.value}>
                    {language.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Input mode
              <select
                value={profileForm.input_mode}
                onChange={(event) => setProfileForm({ ...profileForm, input_mode: event.target.value })}
              >
                <option value="text">Text</option>
                <option value="voice">Voice</option>
              </select>
            </label>
            <div className="profile-actions">
              <button className="primary-button" type="submit" disabled={!canUseProtectedFeatures || loadingKey === "profile"}>
                {loadingKey === "profile" ? "Saving..." : "Save profile"}
              </button>
              <p>Protected routes unlock after login. Profile data improves eligibility explanations.</p>
            </div>
          </form>
        </section>

        <section className="panel search-panel">
          <div className="panel-heading">
            <span className="panel-kicker">3. Scheme Discovery</span>
            <h2>Find the closest matches</h2>
          </div>
          <form className="search-bar" onSubmit={handleSchemeSearch}>
            <input
              value={schemeQuery}
              onChange={(event) => setSchemeQuery(event.target.value)}
              placeholder="Describe the support you need"
            />
            <button className="primary-button" type="submit" disabled={!canUseProtectedFeatures || loadingKey === "search"}>
              {loadingKey === "search" ? "Searching..." : "Search schemes"}
            </button>
          </form>

          <div className="scheme-list">
            {schemeCards.length === 0 ? (
              <div className="empty-state">
                <strong>No scheme results yet.</strong>
                <p>Search after logging in to see profile-aware matches and eligibility notes.</p>
              </div>
            ) : (
              schemeCards.map((result) => (
                <article
                  key={result.scheme.id}
                  className={`scheme-card ${activeSchemeId === result.scheme.id ? "scheme-card-active" : ""}`}
                  onClick={() => setActiveSchemeId(result.scheme.id)}
                >
                  <div className="scheme-card-topline">
                    <span>{result.scheme.level ?? "Unknown level"}</span>
                    <strong>{Math.round(result.relevance_score * 100)}% match</strong>
                  </div>
                  <h3>{result.scheme.scheme_name}</h3>
                  <p>{result.shortDetails}</p>
                  <div className="scheme-detail-block">
                    <strong>Benefits</strong>
                    <p>{result.shortBenefits}</p>
                  </div>
                  <div className="scheme-detail-block">
                    <strong>Eligibility</strong>
                    <p>{result.shortEligibility}</p>
                  </div>
                  {result.eligibility_explanation ? (
                    <div className="eligibility-note">
                      <strong>Profile check</strong>
                      <p>{result.eligibility_explanation}</p>
                    </div>
                  ) : null}
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      void handleCreateApplication(result.scheme.id);
                    }}
                    disabled={!canUseProtectedFeatures || loadingKey === `application-${result.scheme.id}`}
                  >
                    {loadingKey === `application-${result.scheme.id}` ? "Creating..." : "Create application draft"}
                  </button>
                </article>
              ))
            )}
          </div>
        </section>

        <section className="panel chat-panel">
          <div className="panel-heading">
            <span className="panel-kicker">4. Guided Assistance</span>
            <h2>Ask the assistant in your preferred language</h2>
          </div>
          <div className="chat-thread">
            {chatHistory.length === 0 ? (
              <div className="empty-state">
                <strong>No chat yet.</strong>
                <p>Ask about eligibility, document needs, or application steps.</p>
              </div>
            ) : (
              chatHistory.map((message, index) => (
                <div key={`${message.role}-${index}`} className={`chat-bubble chat-${message.role}`}>
                  <span>{message.role === "user" ? "Citizen" : "SevaSetu AI"}</span>
                  <p>{message.content}</p>
                </div>
              ))
            )}
          </div>
          <form className="chat-composer" onSubmit={handleChat}>
            <textarea
              value={chatMessage}
              onChange={(event) => setChatMessage(event.target.value)}
              rows={4}
              placeholder="Explain which schemes match my profile and what documents I may need."
            />
            <button className="primary-button" type="submit" disabled={!canUseProtectedFeatures || loadingKey === "chat"}>
              {loadingKey === "chat" ? "Sending..." : "Send message"}
            </button>
          </form>
        </section>

        <section className="panel applications-panel">
          <div className="panel-heading">
            <span className="panel-kicker">5. Tracking</span>
            <h2>Application drafts and readiness</h2>
          </div>
          {applications.length === 0 ? (
            <div className="empty-state">
              <strong>No application drafts yet.</strong>
              <p>Create one from a scheme card to track status and notes.</p>
            </div>
          ) : (
            <div className="application-list">
              {applications.map((application) => (
                <article key={application.id} className="application-card">
                  <div className="application-status">{application.status}</div>
                  <h3>{application.scheme?.scheme_name ?? "Unnamed scheme"}</h3>
                  <p>{application.notes ?? "No notes available."}</p>
                  <div className="application-meta">
                    <span>Score: {application.eligibility_score?.toFixed(2) ?? "N/A"}</span>
                    <span>Updated: {new Date(application.updated_at).toLocaleString()}</span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function truncateText(value: string | null, limit = 180) {
  if (!value) {
    return "No details available in the current dataset.";
  }

  if (value.length <= limit) {
    return value;
  }

  return `${value.slice(0, limit).trimEnd()}...`;
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return "Something went wrong.";
}

export default App;
