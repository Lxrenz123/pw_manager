<script>
    import { navigate } from "svelte-routing";
    import { apiBase } from "../script/api-base-url";
    import { deriveKey } from "../script/crypto.js";
    import { userKey } from "../stores/user-key.js";

    let email = "";
    let password = "";
    let result = "";


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

    }

    localStorage.setItem("access_token", data.access_token);

    const salt = Uint8Array.from(atob(data.user.salt), c => c.charCodeAt(0));
    const encryptedUserKey = Uint8Array.from(atob(data.user.user_key), c => c.charCodeAt(0));
    const iv = Uint8Array.from(atob(data.user.iv), c => c.charCodeAt(0));

    const { key: derivedKey } = await deriveKey(password, salt);

    const decrypted_user_key = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv},
        derivedKey,
        encryptedUserKey
    );


    const importedUserKey = await crypto.subtle.importKey(
    "raw",
    decrypted_user_key,
    { name: "AES-GCM" },
    true,
    ["encrypt", "decrypt"]
);

    userKey.set(importedUserKey);


    navigate("/app");
    return "Successfully logged in!";

    
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
            <p class="subtitle">// Secure Password Management System</p>
        </div>

        {#if result}
            <div class="alert error">
                <span class="icon">⚠</span>
                {result}
            </div>
        {/if}

        <form class="login-form" on:submit|preventDefault={login}>
            <div class="form-group">
                <label for="username" class="label">
                    <span class="prompt">root@cipher:~$</span> enter_email
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
                    <span class="prompt">root@cipher:~$</span> enter_password
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


