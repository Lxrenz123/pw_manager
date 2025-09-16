<script>
    import { navigate } from "svelte-routing";
    import { apiBase } from "../script/api-base-url";
    import { deriveKey } from "../script/crypto.js";
    import { userKey } from "../stores/user-key.js";
    import { loginCrypto } from "../script/crypto.js";


    let preauth_token;
    let userData;
    let mfaCode = $state("");
    let showMFA = $state(false);

    async function verify2FA(){
        result = "";


        preauth_token = localStorage.getItem("preauth_token");
        const response = await fetch(`${apiBase}/auth/2fa-verify`, {
        method: "POST",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        },
        body: JSON.stringify({"preauth_token": preauth_token, "code": mfaCode})
    
    });

        const data = await response.json();

        if (!response.ok){

            result = data.detail || "2FA verification failed";
            return;
        }

 

        return loginCrypto(data, password)
    }



    let email = $state("");
    let password = "";
    let result = $state("");


    async function login(){
    const response = await fetch( `${apiBase}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'accept': "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    
    if (!response.ok){

        result = data.detail;
        throw new Error("Failed");
        return;
    }

    if (data.mfa_required){

        localStorage.setItem("preauth_token", data.preauth_token)
        
        showMFA = true;
        return {"MFA required: ": data.mfa_required}
    }


    return loginCrypto(data, password)

    
}


</script>

<main>
    <div class="login-container">
        <div class="header">
            <h1 class="title">
                <span class="brackets">[</span>
                <span class="text">Password123</span>
                <span class="brackets">]</span>
            </h1>
            {#if showMFA}
                <p class="subtitle">// Two-Factor Authentication Required</p>
            {:else}
                <p class="subtitle">// Secure Password Management System</p>
            {/if}
        </div>

        {#if result}
            <div class="alert error">
                <span class="icon">⚠</span>
                {result}
            </div>
        {/if}

        {#if !showMFA}
            <form class="login-form" on:submit|preventDefault={login} method="POST">
                <div class="form-group">
                    <label for="username" class="label">
                        <span class="prompt">root@password123:~$</span> enter_email
                    </label>
                    <input 
                        id="username" 
                        name="username" 
                        type="email" 
                        placeholder="user@domain.tld"
                        bind:value={email}
                        class="input"
                        required
                    />
                </div>

                <div class="form-group">
                    <label for="password" class="label">
                        <span class="prompt">root@password123:~$</span> enter_password
                    </label>
                    <input 
                        type="password" 
                        name="password" 
                        id="password" 
                        placeholder="••••••••••••"
                        bind:value={password}
                        class="input"
                        required
                    />
                </div>
                

                <button type="submit" class="submit-btn">
                    <span class="btn-text">./authenticate.sh</span>
                    <span class="btn-arrow">→</span>
                </button>
            </form>
        {/if}
        
        {#if showMFA}
            <div class="mfa-section">
                <div class="mfa-header">
                    <h2 class="mfa-title">
                        <span class="mfa-icon">🔐</span>
                        Two-Factor Authentication
                    </h2>
                    <p class="mfa-subtitle">// Enter the 6-digit code from your authenticator app</p>
                </div>
                
                <form class="mfa-form" on:submit|preventDefault={verify2FA}>
                    <div class="form-group">
                        <label for="mfa-code" class="label mfa-label">
                            <span class="prompt">root@password123:~$</span> enter_2fa_code
                        </label>
                        <input 
                            id="mfa-code" 
                            name="mfa-code" 
                            type="text"
                            placeholder="000000"
                            bind:value={mfaCode}
                            class="input mfa-input"
                            maxlength="6"
                            required
                        />
                    </div>
                    
                    <button type="submit" class="submit-btn mfa-btn">
                        <span class="btn-text">./verify_2fa.sh</span>
                        <span class="btn-arrow">✓</span>
                    </button>
                    
                    <button 
                        type="button" 
                        class="back-btn" 
                        on:click={() => { showMFA = false; mfaCode = ""; result = ""; }}
                    >
                        <span class="btn-text">← Back to Login</span>
                    </button>
                </form>
            </div>
        {/if}
        <div class="footer">
            <a href="/register" class="register-link">
                <span class="prompt">></span> create_new_account()
            </a>
        </div>
    </div>
</main>


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

    .login-container {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #00ff41;
        border-radius: 10px;
        padding: 40px;
        width: 100%;
        max-width: 450px;
        box-shadow: 
            0 0 30px rgba(0, 255, 65, 0.3),
            inset 0 0 20px rgba(0, 255, 65, 0.05);
        backdrop-filter: blur(10px);
        position: relative;
        animation: glowPulse 2s ease-in-out infinite alternate;
    }

    @keyframes glowPulse {
        from {
            box-shadow: 
                0 0 30px rgba(0, 255, 65, 0.3),
                inset 0 0 20px rgba(0, 255, 65, 0.05);
        }
        to {
            box-shadow: 
                0 0 40px rgba(0, 255, 65, 0.5),
                inset 0 0 30px rgba(0, 255, 65, 0.1);
        }
    }

    .header {
        text-align: center;
        margin-bottom: 30px;
    }

    .title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 10px 0;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.8);
    }

    .brackets {
        color: #ff6b6b;
        font-weight: 500;
    }

    .text {
        color: #00ff41;
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
        color: #00ff41;
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
        color: #00ff41;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-sizing: border-box;
    }

    .input:focus {
        outline: none;
        border-color: #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.4);
        background: rgba(0, 0, 0, 0.8);
    }

    .input::placeholder {
        color: #666;
    }

    .submit-btn {
        width: 100%;
        padding: 15px;
        background: linear-gradient(45deg, #00ff41, #00cc33);
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
        box-shadow: 0 5px 15px rgba(0, 255, 65, 0.3);
    }

    .submit-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 20px rgba(0, 255, 65, 0.5);
        background: linear-gradient(45deg, #00cc33, #00ff41);
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

    /* 2FA Section Styles */
    .mfa-section {
        margin-top: 0;
        padding-top: 0;
        animation: slideIn 0.5s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .mfa-header {
        text-align: center;
        margin-bottom: 25px;
    }

    .mfa-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 8px 0;
        color: #00aaff;
        text-shadow: 0 0 15px rgba(0, 170, 255, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }

    .mfa-icon {
        font-size: 1.3rem;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { 
            transform: scale(1);
            opacity: 1;
        }
        50% { 
            transform: scale(1.1);
            opacity: 0.8;
        }
    }

    .mfa-subtitle {
        color: #888;
        font-size: 0.85rem;
        margin: 0;
        font-style: italic;
    }

    .mfa-label {
        color: #00aaff;
    }

    .mfa-input {
        text-align: center;
        letter-spacing: 0.8rem;
        font-size: 1.8rem;
        color: #00aaff;
        border-color: #00aaff;
        background: rgba(0, 0, 0, 0.8);
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 170, 255, 0.5);
    }

    .mfa-input:focus {
        border-color: #00aaff;
        box-shadow: 
            0 0 20px rgba(0, 170, 255, 0.4),
            inset 0 0 10px rgba(0, 170, 255, 0.1);
        background: rgba(0, 0, 0, 0.9);
    }

    .mfa-input::placeholder {
        color: #444;
        letter-spacing: 0.8rem;
        opacity: 0.7;
    }

    .mfa-btn {
        background: linear-gradient(45deg, #00aaff, #0088cc);
        box-shadow: 0 5px 15px rgba(0, 170, 255, 0.3);
        border: 1px solid #00aaff;
        margin-bottom: 15px;
    }

    .mfa-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 20px rgba(0, 170, 255, 0.5);
        background: linear-gradient(45deg, #0088cc, #00aaff);
    }

    .mfa-btn .btn-arrow {
        font-size: 1.1rem;
        color: #000;
    }

    .back-btn {
        width: 100%;
        padding: 12px;
        background: rgba(136, 136, 136, 0.1);
        border: 1px solid #666;
        border-radius: 5px;
        color: #888;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .back-btn:hover {
        background: rgba(136, 136, 136, 0.2);
        color: #bbb;
        border-color: #888;
        transform: translateY(-1px);
    }

    /* Responsive adjustments for 2FA */
    @media (max-width: 480px) {
        .mfa-title {
            font-size: 1.2rem;
        }
        
        .mfa-input {
            font-size: 1.5rem;
            letter-spacing: 0.5rem;
        }
    }

    .footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #333;
    }

    .register-link {
        color: #00aaff;
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        display: inline-block;
    }

    .register-link:hover {
        color: #00ff41;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.8);
        transform: translateX(5px);
    }

    .register-link .prompt {
        color: #ff6b6b;
    }

    /* Matrix rain effect */
    .login-container::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, transparent 30%, rgba(0, 255, 65, 0.1) 50%, transparent 70%);
        border-radius: 10px;
        animation: matrixScan 3s linear infinite;
        z-index: -1;
    }

    @keyframes matrixScan {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
</style>


