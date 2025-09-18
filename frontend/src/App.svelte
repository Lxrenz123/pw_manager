<script>
  import { Router, Link, Route, navigate } from "svelte-routing";
  import Register from './pages/Register.svelte';
  import Login from './pages/Login.svelte'; 
  import App from './pages/App.svelte';
  import { documentSchema, noteSchema, credentialSchema} from './script/schema.js'

</script>

<Router>
  <Route path="/">
    <!-- Welcome/README Page -->
    <main class="welcome-container">
      <div class="welcome-content">
        <!-- Header -->
        <header class="welcome-header">
          <h1 class="main-title">
            <span class="brackets">[</span>
            <span class="title-text">Password123</span>
            <span class="brackets">]</span>
          </h1>
          <p class="subtitle">// Military-Grade Password Management System</p>
        </header>

        <!-- README Content -->
        <section class="readme-section">
          <div class="readme-content">
            <h2 class="section-title">$ cat README.md</h2>
            
            <div class="readme-text">
              <div class="feature-block">
                <h3 class="feature-title">## OVERVIEW</h3>
                <p>
                  Password123 is an advanced, zero-knowledge password management system designed for 
                  cybersecurity professionals and privacy-conscious users. Built with military-grade 
                  encryption and a terminal-inspired interface.
                </p>
              </div>

              <div class="feature-block">
                <h3 class="feature-title">## SECURITY FEATURES</h3>
                <ul class="feature-list">
                  <li><span class="bullet">></span> **AES-GCM 256-bit Encryption** - Industry standard symmetric encryption</li>
                  <li><span class="bullet">></span> **Zero-Knowledge Architecture** - Your master key never leaves your device</li>
                  <li><span class="bullet">></span> **Client-Side Cryptography** - All encryption/decryption happens locally</li>
                  <li><span class="bullet">></span> **Secure Vault System** - Organize secrets into encrypted containers</li>
                  <li><span class="bullet">></span> **File Encryption** - Store documents, PDFs, and images securely</li>
                </ul>
              </div>

              <div class="feature-block">
                <h3 class="feature-title">## SUPPORTED DATA TYPES</h3>
                <div class="data-types">
                  <div class="data-type">
                    <span class="type-icon">🔑</span>
                    <div>
                      <strong>Credentials</strong>
                      <p>Login credentials with username, password, URL, and notes</p>
                    </div>
                  </div>
                  <div class="data-type">
                    <span class="type-icon">📝</span>
                    <div>
                      <strong>Secure Notes</strong>
                      <p>Encrypted text notes for sensitive information</p>
                    </div>
                  </div>
                  <div class="data-type">
                    <span class="type-icon">📄</span>
                    <div>
                      <strong>Documents</strong>
                      <p>PDF files, images, and text documents (up to 10MB)</p>
                    </div>
                  </div>
                </div>
              </div>

              <div class="feature-block">
                <h3 class="feature-title">## TECHNICAL SPECIFICATIONS</h3>
                <div class="tech-specs">
                  <div class="spec-row">
                    <span class="spec-label">Encryption Algorithm:</span>
                    <span class="spec-value">AES-GCM-256</span>
                  </div>
                  <div class="spec-row">
                    <span class="spec-label">Key Derivation:</span>
                    <span class="spec-value">PBKDF2-SHA256</span>
                  </div>
                  <div class="spec-row">
                    <span class="spec-label">Frontend Framework:</span>
                    <span class="spec-value">Svelte 5.0</span>
                  </div>
                  <div class="spec-row">
                    <span class="spec-label">Backend API:</span>
                    <span class="spec-value">FastAPI + PostgreSQL</span>
                  </div>
                  <div class="spec-row">
                    <span class="spec-label">Authentication:</span>
                    <span class="spec-value">JWT Tokens</span>
                  </div>
                </div>
              </div>

              <div class="feature-block">
                <h3 class="feature-title">## GETTING STARTED</h3>
                <div class="getting-started">
                  <div class="step">
                    <span class="step-number">1.</span>
                    <span>Create your account with a strong master password</span>
                  </div>
                  <div class="step">
                    <span class="step-number">2.</span>
                    <span>Your encryption key is derived from your master password</span>
                  </div>
                  <div class="step">
                    <span class="step-number">3.</span>
                    <span>Create vaults to organize your encrypted secrets</span>
                  </div>
                  <div class="step">
                    <span class="step-number">4.</span>
                    <span>Store credentials, notes, and documents securely</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Action Buttons -->
        <section class="action-section">
          <div class="action-buttons">
            <a href="/login" class="action-btn primary">
              <span class="btn-text">./login.sh</span>
              <span class="btn-arrow">→</span>
            </a>
            <a href="/register" class="action-btn secondary">
              <span class="btn-text">./register.sh</span>
              <span class="btn-arrow">→</span>
            </a>
          </div>
        </section>

        <!-- Footer -->
        <footer class="welcome-footer">
          <p class="footer-text">
            <span class="prompt">root@password123:~$</span> 
            Secure your digital life with military-grade encryption
          </p>
        </footer>
      </div>
    </main>
  </Route>
  
  <Route path="/login">
    <Login />
  </Route>
  <Route path="/register">
    <Register />
  </Route>
  <Route path="/app">
  <App />
  </Route>
</Router>

<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    color: #00ff41;
    min-height: 100vh;
    overflow-x: hidden;
  }

  .welcome-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    position: relative;
  }

  .welcome-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
      radial-gradient(circle at 20% 80%, rgba(0, 255, 65, 0.05) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(0, 150, 255, 0.05) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(255, 107, 107, 0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: -1;
  }

  .welcome-content {
    max-width: 900px;
    width: 100%;
    background: rgba(0, 0, 0, 0.8);
    border: 2px solid #00ff41;
    border-radius: 15px;
    padding: 40px;
    box-shadow: 
      0 0 40px rgba(0, 255, 65, 0.3),
      inset 0 0 30px rgba(0, 255, 65, 0.05);
    backdrop-filter: blur(10px);
    animation: glowPulse 3s ease-in-out infinite alternate;
  }

  @keyframes glowPulse {
    from {
      box-shadow: 
        0 0 40px rgba(0, 255, 65, 0.3),
        inset 0 0 30px rgba(0, 255, 65, 0.05);
    }
    to {
      box-shadow: 
        0 0 60px rgba(0, 255, 65, 0.5),
        inset 0 0 40px rgba(0, 255, 65, 0.1);
    }
  }

  /* Header */
  .welcome-header {
    text-align: center;
    margin-bottom: 40px;
    padding-bottom: 30px;
    border-bottom: 1px solid #333;
  }

  .main-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 0 0 15px 0;
    text-shadow: 0 0 25px rgba(0, 255, 65, 0.8);
  }

  .brackets {
    color: #ff6b6b;
    font-weight: 500;
  }

  .title-text {
    color: #00ff41;
  }

  .subtitle {
    color: #888;
    font-size: 1.1rem;
    margin: 0;
    font-style: italic;
  }

  /* README Section */
  .readme-section {
    margin-bottom: 40px;
  }

  .section-title {
    color: #00aaff;
    font-size: 1.2rem;
    margin: 0 0 25px 0;
    font-weight: 500;
  }

  .feature-block {
    margin-bottom: 30px;
    padding: 20px;
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid #333;
    border-radius: 8px;
  }

  .feature-title {
    color: #ff6b6b;
    font-size: 1rem;
    margin: 0 0 15px 0;
    font-weight: 500;
    text-transform: uppercase;
  }

  .feature-block p {
    color: #ccc;
    line-height: 1.6;
    margin: 0;
  }

  .feature-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .feature-list li {
    color: #ccc;
    margin: 8px 0;
    display: flex;
    align-items: flex-start;
    gap: 10px;
  }

  .bullet {
    color: #00ff41;
    font-weight: 500;
  }

  /* Data Types */
  .data-types {
    display: grid;
    gap: 15px;
  }

  .data-type {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    padding: 15px;
    background: rgba(0, 0, 0, 0.6);
    border: 1px solid #444;
    border-radius: 5px;
  }

  .type-icon {
    font-size: 1.5rem;
  }

  .data-type strong {
    color: #00aaff;
    display: block;
    margin-bottom: 5px;
  }

  .data-type p {
    color: #888;
    margin: 0;
    font-size: 0.9rem;
  }

  /* Tech Specs */
  .tech-specs {
    display: grid;
    gap: 10px;
  }

  .spec-row {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 15px;
    padding: 8px 0;
    border-bottom: 1px solid #333;
  }

  .spec-label {
    color: #888;
    font-size: 0.9rem;
  }

  .spec-value {
    color: #00ff41;
    font-weight: 500;
    font-size: 0.9rem;
  }

  /* Getting Started */
  .getting-started {
    display: grid;
    gap: 12px;
  }

  .step {
    display: flex;
    align-items: center;
    gap: 15px;
    color: #ccc;
    font-size: 0.9rem;
  }

  .step-number {
    background: rgba(0, 170, 255, 0.2);
    color: #00aaff;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    font-size: 0.8rem;
  }

  /* Action Section */
  .action-section {
    margin-bottom: 30px;
  }

  .action-buttons {
    display: flex;
    gap: 20px;
    justify-content: center;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 15px 25px;
    border-radius: 8px;
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
    transition: all 0.3s ease;
    text-transform: uppercase;
  }

  .action-btn.primary {
    background: linear-gradient(45deg, #00ff41, #00cc33);
    color: #000;
    box-shadow: 0 5px 20px rgba(0, 255, 65, 0.3);
  }

  .action-btn.secondary {
    background: linear-gradient(45deg, #00aaff, #0088cc);
    color: #000;
    box-shadow: 0 5px 20px rgba(0, 170, 255, 0.3);
  }

  .action-btn:hover {
    transform: translateY(-3px);
  }

  .action-btn.primary:hover {
    box-shadow: 0 8px 25px rgba(0, 255, 65, 0.5);
  }

  .action-btn.secondary:hover {
    box-shadow: 0 8px 25px rgba(0, 170, 255, 0.5);
  }

  .btn-arrow {
    font-size: 1.2rem;
    transition: transform 0.3s ease;
  }

  .action-btn:hover .btn-arrow {
    transform: translateX(5px);
  }

  /* Footer */
  .welcome-footer {
    text-align: center;
    padding-top: 30px;
    border-top: 1px solid #333;
  }

  .footer-text {
    color: #666;
    margin: 0;
    font-size: 0.9rem;
  }

  .prompt {
    color: #ff6b6b;
    font-weight: 500;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .main-title {
      font-size: 2rem;
    }

    .welcome-content {
      padding: 30px 20px;
    }

    .action-buttons {
      flex-direction: column;
      align-items: center;
    }

    .action-btn {
      width: 100%;
      max-width: 250px;
      justify-content: center;
    }

    .spec-row {
      grid-template-columns: 1fr;
      gap: 5px;
    }

    .data-type {
      flex-direction: column;
      text-align: center;
    }
  }
</style>

