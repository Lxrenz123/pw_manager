<script>
    import { apiBase } from "../script/api-base-url";
    import { deriveKey } from "../script/crypto.js";

    let email = "";
    let password = "";
    let confirmPassword = "";
    let user_key;
    let result = "";
    let isSuccess = false;





async function register(){
    // Reset previous messages
    result = "";
    isSuccess = false;

    // Validate password confirmation
    if (password !== confirmPassword) {
        result = "Password confirmation does not match";
        return;
    }

    if (password.length < 8) {
        result = "Password must be at least 8 characters long";
        return;
    }

    try {
        const salt = crypto.getRandomValues(new Uint8Array(16));
     
        const { key: derivedKey } = await deriveKey(password, salt)

        const userKeyBytes = crypto.getRandomValues(new Uint8Array(32));

        const iv = crypto.getRandomValues(new Uint8Array(12));
        const encryptedUserKey = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv},
            derivedKey,
            userKeyBytes
        );

        const encryptedUserKeyBase64 = btoa(String.fromCharCode(...new Uint8Array(encryptedUserKey)));
        const ivBase64 = btoa(String.fromCharCode(...iv));

        
        const response = await fetch(`${apiBase}/user/`, {
            method: "POST",
            headers: {
            'Content-Type': "application/json",
            'accept': "application/json"
            },
            body: JSON.stringify({email, password, user_key: encryptedUserKeyBase64, salt: btoa(String.fromCharCode(...salt)), iv: ivBase64})
        });

        const data = await response.json();

        if (!response.ok){
            result = data.detail;
            isSuccess = false;
            return;
        }

        // Success!
        isSuccess = true;
        result = "User registered successfully! Redirecting to login...";
        
        // Clear form
        email = "";
        password = "";
        confirmPassword = "";
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
            window.location.href = "/login";
        }, 2000);

    } catch (error) {
        console.error("Registration error:", error);
        result = "Registration failed. Please try again.";
        isSuccess = false;
    }
}


</script>

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

    main {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        position: relative;
    }

    main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 80%, rgba(0, 255, 65, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(0, 150, 255, 0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }

    .register-container {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #00aaff;
        border-radius: 10px;
        padding: 40px;
        width: 100%;
        max-width: 450px;
        box-shadow: 
            0 0 30px rgba(0, 170, 255, 0.3),
            inset 0 0 20px rgba(0, 170, 255, 0.05);
        backdrop-filter: blur(10px);
        position: relative;
        animation: glowPulse 2s ease-in-out infinite alternate;
    }

    @keyframes glowPulse {
        from {
            box-shadow: 
                0 0 30px rgba(0, 170, 255, 0.3),
                inset 0 0 20px rgba(0, 170, 255, 0.05);
        }
        to {
            box-shadow: 
                0 0 40px rgba(0, 170, 255, 0.5),
                inset 0 0 30px rgba(0, 170, 255, 0.1);
        }
    }

    .header {
        text-align: center;
        margin-bottom: 30px;
    }

    .title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 10px 0;
        text-shadow: 0 0 20px rgba(0, 170, 255, 0.8);
        line-height: 1.2;
    }

    .brackets {
        color: #ff6b6b;
        font-weight: 500;
    }

    .text {
        color: #00aaff;
    }

    .subtitle {
        color: #888;
        font-size: 0.9rem;
        margin: 0;
        font-style: italic;
    }

    .alert {
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid #ff6b6b;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .alert.error {
        color: #ff6b6b;
    }

    .alert.success {
        background: rgba(0, 255, 65, 0.1);
        border-color: #00ff41;
        color: #00ff41;
    }

    .icon {
        font-size: 1.2rem;
    }

    .form-group {
        margin-bottom: 25px;
    }

    .label {
        display: block;
        margin-bottom: 8px;
        font-size: 0.9rem;
        color: #00aaff;
    }

    .prompt {
        color: #ff6b6b;
        font-weight: 500;
    }

    .input {
        width: 100%;
        padding: 15px;
        background: rgba(0, 0, 0, 0.6);
        border: 2px solid #333;
        border-radius: 5px;
        color: #00aaff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-sizing: border-box;
    }

    .input:focus {
        outline: none;
        border-color: #00aaff;
        box-shadow: 0 0 15px rgba(0, 170, 255, 0.4);
        background: rgba(0, 0, 0, 0.8);
    }

    .input::placeholder {
        color: #666;
    }

    .password-help {
        margin-top: 5px;
    }

    .help-text {
        color: #666;
        font-size: 0.8rem;
        font-style: italic;
    }

    .submit-btn {
        width: 100%;
        padding: 15px;
        background: linear-gradient(45deg, #00aaff, #0088cc);
        border: none;
        border-radius: 5px;
        color: #000;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        text-transform: uppercase;
        box-shadow: 0 5px 15px rgba(0, 170, 255, 0.3);
    }

    .submit-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 20px rgba(0, 170, 255, 0.5);
        background: linear-gradient(45deg, #0088cc, #00aaff);
    }

    .submit-btn:active {
        transform: translateY(0);
    }

    .btn-arrow {
        font-size: 1.2rem;
        transition: transform 0.3s ease;
    }

    .submit-btn:hover .btn-arrow {
        transform: translateX(5px);
    }

    .footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #333;
    }

    .login-link {
        color: #00ff41;
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        display: inline-block;
    }

    .login-link:hover {
        color: #00aaff;
        text-shadow: 0 0 10px rgba(0, 170, 255, 0.8);
        transform: translateX(5px);
    }

    .login-link .prompt {
        color: #ff6b6b;
    }

    /* Scanning effect */
    .register-container::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, transparent 30%, rgba(0, 170, 255, 0.1) 50%, transparent 70%);
        border-radius: 10px;
        animation: scanEffect 3s linear infinite;
        z-index: -1;
    }

    @keyframes scanEffect {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
</style>

<main>
    <div class="register-container">
        <div class="header">
            <h1 class="title">
                <span class="brackets">[</span>
                <span class="text">New User Registration</span>
                <span class="brackets">]</span>
            </h1>
            <p class="subtitle">// Initialize new secure identity</p>
        </div>

        {#if result}
            <div class="alert" class:success={isSuccess} class:error={!isSuccess}>
                <span class="icon">{isSuccess ? '✓' : '⚠'}</span>
                {result}
            </div>
        {/if}

        <form class="register-form" on:submit|preventDefault={register}>
            <div class="form-group">
                <label for="username" class="label">
                    <span class="prompt">admin@vault:~$</span> set_email
                </label>
                <input 
                    id="username" 
                    name="username" 
                    type="email" 
                    placeholder="user@secure.domain"
                    bind:value={email}
                    class="input"
                    required
                />
            </div>

            <div class="form-group">
                <label for="password" class="label">
                    <span class="prompt">admin@vault:~$</span> set_master_key
                </label>
                <input 
                    name="password" 
                    type="password" 
                    id="password" 
                    placeholder="••••••••••••••••"
                    bind:value={password}
                    class="input"
                    required
                    minlength="8"
                />
            </div>

            <div class="form-group">
                <label for="confirm-password" class="label">
                    <span class="prompt">admin@vault:~$</span> confirm_master_key
                </label>
                <input 
                    name="confirm-password" 
                    type="password" 
                    id="confirm-password" 
                    placeholder="••••••••••••••••"
                    bind:value={confirmPassword}
                    class="input"
                    required
                    minlength="8"
                />
                <div class="password-help">
                    <span class="help-text">
                        // Use strong master key (min 8 chars)
                    </span>
                </div>
            </div>

            <button type="submit" class="submit-btn">
                <span class="btn-text">./REGISTER_USER.sh</span>
                <span class="btn-arrow">→</span>
            </button>
        </form>

        <div class="footer">
            <a href="/login" class="login-link">
                <span class="prompt">></span> access_existing_vault()
            </a>
        </div>
    </div>
</main>
