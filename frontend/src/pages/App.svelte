<script>
    import { onMount } from "svelte";
    import { apiBase } from "../script/api-base-url";
    import { credentialSchema } from "../script/schema";
    import { userKey} from "../stores/user-key.js"
    import { get } from "svelte/store";
    import { navigate } from "svelte-routing";

    let newNote;
    let newCredential;
    let newDocument;
    
    let plaintext;

    let vaults = $state([]);
    let vaultName = $state("");

    let secrets = $state([]);
    
    let title = $state("");
    let data_plaintext = $state("");
    let data_encrypted = $state("");
    let selectedVaultId = $state(null); 

    let username = "";
    let password = "";
    let url = "";
    let note = "";
    let doc = ""
    let activeSecretType = $state("note"); // Track which form is active

    function logout() {
        localStorage.removeItem("access_token");
        userKey.set(null);
        navigate("/login");
    }


    onMount(async () => {
        // Check authentication
        const token = localStorage.getItem("access_token");
        if (!token) {
            navigate("/login");
            return;
        }

        getVaults();
        const userKeyValue = get(userKey);
        console.log("UserKey at addSecret:", userKeyValue);
    });

async function getVaults(){
    const response = await fetch(`${apiBase}/vault/`, {
                        method: "GET",
                        headers: {
                        'Content-Type': 'application/json',
                        'accept': "application/json",
                        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                        }
                    }
                    )
    vaults = await response.json();
    
    if (!response.ok){
        throw new Error("Network error");
    }

}

async function addVault(){
       const response = await fetch(`${apiBase}/vault/`, {
                        method: "POST",
                        headers: {
                        'Content-Type': 'application/json',
                        'accept': "application/json",
                        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                        },
                        body: JSON.stringify({name: vaultName})
                    }
                    )
    if (!response.ok){
        throw new Error("Network error");
    }

    const newVault = await response.json()
    vaults.push(newVault)
    vaultName = "";

}

async function getSecretsOfVault(vaultId){
    const response = await fetch(`${apiBase}/secret/${vaultId}`, {
        method: "GET",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        }
    })

    if (!response.ok){
        throw new Error("Network error");
    }
    const encryptedSecrets = await response.json(); 
    selectedVaultId = vaultId;



    secrets = await Promise.all(encryptedSecrets.map(async (secret) => {
       try {
          
            const encSecretKeyBytes = Uint8Array.from(atob(secret.encrypted_secret_key), c => c.charCodeAt(0));
            const ivKey = Uint8Array.from(atob(secret.secret_key_iv), c => c.charCodeAt(0));

            
          const userKeyValue = get(userKey);
          
            const secretKeyBytes = await crypto.subtle.decrypt(
                { name: "AES-GCM", iv: ivKey },
                userKeyValue,
                encSecretKeyBytes
            );

            const secretKey = await crypto.subtle.importKey(
                "raw",
                secretKeyBytes,
                { name: "AES-GCM" },
                false,
                ["encrypt", "decrypt"]
            );

     
            const ivData = Uint8Array.from(atob(secret.secret_iv), c => c.charCodeAt(0));
            const encryptedData = Uint8Array.from(atob(secret.data_encrypted), c => c.charCodeAt(0));

            const decryptedData = await crypto.subtle.decrypt(
                { name: "AES-GCM", iv: ivData },
                secretKey,
                encryptedData
            );

            const decoder = new TextDecoder();
            const plaintext = decoder.decode(decryptedData);

            return { ...secret, data: JSON.parse(plaintext) };

        } catch (err) {
            
            console.error("Decrypt failed for secret:", err);
            navigate("/login");
            return { ...secret, data: null };

        }
    }));

    
}


async function addSecret(secret_type){

   newCredential = {
    username: username,
    password: password,
    url: url,
    note: note
   }
   newNote = {
    content: note
   }
   newDocument = {
    file: doc

   }

   const secretKeyBytes = crypto.getRandomValues(new Uint8Array(32));
   const secretKey = await crypto.subtle.importKey(
   "raw",
   secretKeyBytes,
   { name: "AES-GCM"},
   true,
   ["encrypt", "decrypt"]
   );

   const encoder = new TextEncoder();
   if (secret_type == "note"){
        plaintext = encoder.encode(JSON.stringify(newNote));
   } else if (secret_type == "credential"){

         plaintext = encoder.encode(JSON.stringify(newCredential));
   }
    else if (secret_type == "document"){

         plaintext = encoder.encode(JSON.stringify(newDocument))
    }
    const secretIv = crypto.getRandomValues(new Uint8Array(12));

    const encryptedSecret = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: secretIv},
        secretKey,
        plaintext
    )

            const userKeyValue = get(userKey);
        if (!userKeyValue || !(userKeyValue instanceof CryptoKey)) {
            throw new Error("User key is not properly initialized as a CryptoKey");
        }

    const secretKeyIv = crypto.getRandomValues(new Uint8Array(12));

    const encryptedSecretKey = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: secretKeyIv },
    userKeyValue,
    secretKeyBytes
    )

    const encryptedSecretB64 = btoa(String.fromCharCode(...new Uint8Array(encryptedSecret)));
    const secretIvB64 = btoa(String.fromCharCode(...secretIv));
    const encryptedSecretKeyB64 = btoa(String.fromCharCode(...new Uint8Array(encryptedSecretKey)));
    const secretKeyIvB64 = btoa(String.fromCharCode(...secretKeyIv));



    const response = await fetch(`${apiBase}/secret/${selectedVaultId}/${secret_type}`, {
        method: "POST",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({            
            title,
            data_encrypted: encryptedSecretB64,
            secret_iv: secretIvB64,
            encrypted_secret_key: encryptedSecretKeyB64,
            secret_key_iv: secretKeyIvB64})
    })

    if (!response.ok){
        throw new Error("Network error");
    }

    const newSecret = await response.json()
    
            

    const decryptedData = secret_type == "note" ? newNote : 
                            secret_type == "credential" ? newCredential : newDocument;
    

    secrets.push({ ...newSecret, data: decryptedData });
            

    // Clear form fields based on secret type
    title = "";
    if (secret_type === "note") {
        note = "";
    } else if (secret_type === "credential") {
        username = "";
        password = "";
        url = "";
        note = "";
    } else if (secret_type === "document") {
        doc = "";
    }
    title = "";
            
 
}




</script>

<div class="app-container">
    <!-- Header -->
    <header class="header">
        <div class="header-content">
            <h1 class="app-title">
                <span class="brackets">[</span>
                <span class="text">Password123</span>
                <span class="brackets">]</span>
            </h1>
            <button class="logout-btn" onclick={logout}>
                <span>logout</span>
                <span class="logout-icon">⏻</span>
            </button>
        </div>
    </header>

    <main class="main-content">
        <!-- Vault Navigation -->
        <aside class="vault-sidebar">
            <div class="vault-header">
                <h2 class="section-title">// SECURE VAULTS</h2>
            </div>
            
            <div class="vault-list">
                {#each vaults as vault}
                    <div class="vault-item">
                        <button 
                            class="vault-btn"
                            class:selected={selectedVaultId === vault.id}
                            onclick={() => getSecretsOfVault(vault.id)}
                        >
                            <span class="vault-icon">🔒</span>
                            <span class="vault-name">{vault.name}</span>
                            <span class="vault-indicator">→</span>
                        </button>
                    </div>
                {/each}
            </div>

            <div class="add-vault-section">
                <div class="input-group">
                    <input 
                        class="vault-input" 
                        placeholder="vault_name" 
                        bind:value={vaultName} 
                    />
                    <button class="add-vault-btn" onclick={addVault}>
                        <span>CREATE</span>
                    </button>
                </div>
            </div>
        </aside>

        <!-- Secrets Content -->
        <section class="secrets-content">
            {#if selectedVaultId}
                <div class="secrets-header">
                    <h2 class="section-title">// ENCRYPTED SECRETS</h2>
                    <div class="vault-status">
                        <span class="status-indicator">●</span>
                        <span>VAULT DECRYPTED</span>
                    </div>
                </div>

                <!-- Add Secret Form -->
                <div class="add-secret-form">
                    <!-- Secret Type Tabs -->
                    <div class="secret-type-tabs">
                        <button 
                            class="tab-btn"
                            class:active={activeSecretType === "note"}
                            onclick={() => activeSecretType = "note"}
                        >
                            <span class="tab-icon">📝</span>
                            <span>NOTE</span>
                        </button>
                        <button 
                            class="tab-btn"
                            class:active={activeSecretType === "credential"}
                            onclick={() => activeSecretType = "credential"}
                        >
                            <span class="tab-icon">🔑</span>
                            <span>CREDENTIAL</span>
                        </button>
                        <button 
                            class="tab-btn"
                            class:active={activeSecretType === "document"}
                            onclick={() => activeSecretType = "document"}
                        >
                            <span class="tab-icon">📄</span>
                            <span>DOCUMENT</span>
                        </button>
                    </div>

                    <!-- Dynamic Form Title -->
                    <h3 class="form-title">$ new_secret --type={activeSecretType}</h3>

                    <!-- Note Form -->
                    {#if activeSecretType === "note"}
                        <div class="form-grid note-form">
                            <input 
                                placeholder="secret_title" 
                                class="secret-input" 
                                bind:value={title} 
                            />
                            <textarea 
                                placeholder="note_content" 
                                class="secret-textarea" 
                                bind:value={note}
                                rows="4"
                            ></textarea>
                            <button class="add-secret-btn" onclick={() => addSecret("note")}>
                                <span>ENCRYPT & STORE</span>
                                <span class="btn-icon">🔐</span>
                            </button>
                        </div>
                    {/if}

                    <!-- Credential Form -->
                    {#if activeSecretType === "credential"}
                        <div class="credential-form">
                            <div class="form-row">
                                <input 
                                    placeholder="secret_title" 
                                    class="secret-input" 
                                    bind:value={title} 
                                />
                            </div>
                            <div class="form-row">
                                <input 
                                    placeholder="username" 
                                    class="secret-input" 
                                    bind:value={username} 
                                />
                                <input 
                                    placeholder="password" 
                                    type="password"
                                    class="secret-input" 
                                    bind:value={password} 
                                />
                            </div>
                            <div class="form-row">
                                <input 
                                    placeholder="website_url (optional)" 
                                    class="secret-input" 
                                    bind:value={url} 
                                />
                            </div>
                            <div class="form-row">
                                <textarea 
                                    placeholder="additional_notes (optional)" 
                                    class="secret-textarea" 
                                    bind:value={note}
                                    rows="2"
                                ></textarea>
                            </div>
                            <button class="add-secret-btn" onclick={() => addSecret("credential")}>
                                <span>ENCRYPT & STORE</span>
                                <span class="btn-icon">🔐</span>
                            </button>
                        </div>
                    {/if}

                    <!-- Document Form -->
                    {#if activeSecretType === "document"}
                        <div class="document-form">
                            <div class="form-row">
                                <input 
                                    placeholder="document_title" 
                                    class="secret-input" 
                                    bind:value={title} 
                                />
                            </div>
                            <div class="form-row">
                                <textarea 
                                    placeholder="document_content_or_description" 
                                    class="secret-textarea" 
                                    bind:value={doc}
                                    rows="4"
                                ></textarea>
                            </div>
                            <button class="add-secret-btn" onclick={() => addSecret("document")}>
                                <span>ENCRYPT & STORE</span>
                                <span class="btn-icon">🔐</span>
                            </button>
                        </div>
                    {/if}
                </div>

                <!-- Secrets List -->
                <div class="secrets-list">
                    {#each secrets as secret}
                        <div class="secret-card">
                            <div class="secret-header">
                                <h4 class="secret-title">{secret.title}</h4>
                                <div class="secret-meta">
                                    <span class="secret-type">
                                        {#if secret.data?.content}
                                            NOTE
                                        {:else if secret.data?.username}
                                            CREDENTIAL
                                        {:else if secret.data?.file}
                                            DOCUMENT
                                        {:else}
                                            DATA
                                        {/if}
                                    </span>
                                    <button class="secret-action">⋯</button>
                                </div>
                            </div>
                            
                            <div class="secret-body">
                                {#if secret.data}
                                    {#if secret.data.content}
                                        <div class="field">
                                            <span class="field-label">content:</span>
                                            <span class="field-value">{secret.data.content}</span>
                                        </div>
                                    {:else if secret.data.username}
                                        <div class="field">
                                            <span class="field-label">username:</span>
                                            <span class="field-value">{secret.data.username}</span>
                                        </div>
                                        <div class="field">
                                            <span class="field-label">password:</span>
                                            <span class="field-value password">{"•".repeat(secret.data.password.length)}</span>
                                        </div>
                                        {#if secret.data.url}
                                            <div class="field">
                                                <span class="field-label">url:</span>
                                                <span class="field-value">{secret.data.url}</span>
                                            </div>
                                        {/if}
                                        {#if secret.data.note}
                                            <div class="field">
                                                <span class="field-label">note:</span>
                                                <span class="field-value">{secret.data.note}</span>
                                            </div>
                                        {/if}
                                    {:else if secret.data.file}
                                        <div class="field">
                                            <span class="field-label">file:</span>
                                            <span class="field-value">{secret.data.file}</span>
                                        </div>
                                    {:else}
                                        <pre class="debug-data">{JSON.stringify(secret.data, null, 2)}</pre>
                                    {/if}
                                {:else}
                                    <div class="error-message">
                                        <span class="error-icon">⚠</span>
                                        <span>DECRYPTION_FAILED</span>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/each}
                </div>
            {:else}
                <div class="empty-state">
                    <div class="empty-icon">🔒</div>
                    <h3>SELECT A VAULT</h3>
                    <p>Choose a vault from the sidebar to decrypt and view your secrets</p>
                </div>
            {/if}
        </section>
    </main>
</div>

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

    .app-container {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }

    /* Header */
    .header {
        background: rgba(0, 0, 0, 0.9);
        border-bottom: 2px solid #00ff41;
        padding: 15px 0;
        position: sticky;
        top: 0;
        z-index: 100;
        backdrop-filter: blur(10px);
    }

    .header-content {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .app-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 0 15px rgba(0, 255, 65, 0.8);
    }

    .brackets {
        color: #ff6b6b;
    }

    .text {
        color: #00ff41;
    }

    .logout-btn {
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid #ff6b6b;
        color: #ff6b6b;
        padding: 8px 15px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .logout-btn:hover {
        background: rgba(255, 107, 107, 0.2);
        transform: translateY(-1px);
    }

    /* Main Content */
    .main-content {
        flex: 1;
        display: grid;
        grid-template-columns: 300px 1fr;
        gap: 20px;
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
        width: 100%;
        box-sizing: border-box;
    }

    /* Vault Sidebar */
    .vault-sidebar {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        height: fit-content;
        position: sticky;
        top: 100px;
    }

    .vault-header, .secrets-header {
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 1rem;
        color: #888;
        margin: 0;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .vault-list {
        margin-bottom: 30px;
    }

    .vault-item {
        margin-bottom: 8px;
    }

    .vault-btn {
        width: 100%;
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid #333;
        color: #00ff41;
        padding: 12px 15px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
        text-align: left;
    }

    .vault-btn:hover {
        background: rgba(0, 255, 65, 0.1);
        border-color: #00ff41;
        transform: translateX(5px);
    }

    .vault-btn.selected {
        background: rgba(0, 255, 65, 0.2);
        border-color: #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
    }

    .vault-icon {
        font-size: 1.1rem;
    }

    .vault-name {
        flex: 1;
    }

    .vault-indicator {
        opacity: 0.5;
        transition: opacity 0.3s ease;
    }

    .vault-btn:hover .vault-indicator,
    .vault-btn.selected .vault-indicator {
        opacity: 1;
    }

    /* Add Vault Section */
    .add-vault-section {
        border-top: 1px solid #333;
        padding-top: 20px;
    }

    .input-group {
        display: flex;
        gap: 10px;
    }

    .vault-input {
        flex: 1;
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #333;
        color: #00ff41;
        padding: 10px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
    }

    .vault-input:focus {
        outline: none;
        border-color: #00ff41;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    }

    .add-vault-btn {
        background: linear-gradient(45deg, #00ff41, #00cc33);
        border: none;
        color: #000;
        padding: 10px 15px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .add-vault-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 255, 65, 0.4);
    }

    /* Secrets Content */
    .secrets-content {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 30px;
        min-height: 600px;
    }

    .secrets-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
    }

    .vault-status {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #00ff41;
        font-size: 0.9rem;
    }

    .status-indicator {
        color: #00ff41;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Add Secret Form */
    .add-secret-form {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #444;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 30px;
    }

    /* Secret Type Tabs */
    .secret-type-tabs {
        display: flex;
        gap: 5px;
        margin-bottom: 20px;
        border-bottom: 1px solid #333;
        padding-bottom: 15px;
    }

    .tab-btn {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid #333;
        color: #888;
        padding: 10px 15px;
        border-radius: 5px 5px 0 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
        text-transform: uppercase;
        font-weight: 500;
    }

    .tab-btn:hover {
        background: rgba(0, 255, 65, 0.1);
        color: #00ff41;
        border-color: #00ff41;
    }

    .tab-btn.active {
        background: rgba(0, 170, 255, 0.2);
        color: #00aaff;
        border-color: #00aaff;
        box-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
    }

    .tab-icon {
        font-size: 1rem;
    }

    .form-title {
        color: #00aaff;
        font-size: 1rem;
        margin: 0 0 20px 0;
        font-weight: 500;
    }

    .form-grid {
        display: grid;
        grid-template-columns: 1fr 2fr auto;
        gap: 15px;
        align-items: start;
    }

    .note-form {
        display: grid;
        grid-template-columns: 1fr 2fr auto;
        gap: 15px;
        align-items: start;
    }

    /* Credential and Document Forms */
    .credential-form, .document-form {
        display: grid;
        gap: 15px;
    }

    .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
    }

    .form-row:has(textarea), .form-row:has(.secret-input:only-child) {
        grid-template-columns: 1fr;
    }

    .secret-input, .secret-textarea {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #333;
        color: #00ff41;
        padding: 12px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        resize: vertical;
    }

    .secret-input:focus, .secret-textarea:focus {
        outline: none;
        border-color: #00aaff;
        box-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
    }

    .add-secret-btn {
        background: linear-gradient(45deg, #00aaff, #0088cc);
        border: none;
        color: #000;
        padding: 12px 20px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
        height: fit-content;
    }

    .add-secret-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 170, 255, 0.4);
    }

    /* Secrets List */
    .secrets-list {
        display: grid;
        gap: 15px;
    }

    .secret-card {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #333;
        border-radius: 8px;
        padding: 20px;
        transition: all 0.3s ease;
    }

    .secret-card:hover {
        border-color: #00ff41;
        box-shadow: 0 5px 20px rgba(0, 255, 65, 0.1);
    }

    .secret-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }

    .secret-title {
        color: #00ff41;
        font-size: 1.1rem;
        margin: 0;
        font-weight: 500;
    }

    .secret-meta {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .secret-type {
        background: rgba(0, 170, 255, 0.2);
        color: #00aaff;
        padding: 4px 8px;
        border-radius: 3px;
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .secret-action {
        background: none;
        border: none;
        color: #666;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 5px;
        border-radius: 3px;
        transition: all 0.3s ease;
    }

    .secret-action:hover {
        color: #00ff41;
        background: rgba(0, 255, 65, 0.1);
    }

    .secret-body {
        display: grid;
        gap: 10px;
    }

    .field {
        display: grid;
        grid-template-columns: 120px 1fr;
        gap: 15px;
        align-items: center;
    }

    .field-label {
        color: #888;
        font-size: 0.9rem;
        text-transform: lowercase;
    }

    .field-value {
        color: #00ff41;
        font-size: 0.9rem;
        word-break: break-all;
    }

    .field-value.password {
        color: #ff6b6b;
        letter-spacing: 2px;
    }

    .debug-data {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #333;
        border-radius: 5px;
        padding: 15px;
        color: #888;
        font-size: 0.8rem;
        overflow-x: auto;
    }

    .error-message {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #ff6b6b;
        font-size: 0.9rem;
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #666;
    }

    .empty-icon {
        font-size: 4rem;
        margin-bottom: 20px;
        opacity: 0.5;
    }

    .empty-state h3 {
        color: #888;
        margin: 0 0 10px 0;
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .empty-state p {
        margin: 0;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-content {
            grid-template-columns: 1fr;
            gap: 20px;
        }

        .vault-sidebar {
            position: static;
        }

        .form-grid, .note-form {
            grid-template-columns: 1fr;
        }

        .form-row {
            grid-template-columns: 1fr;
        }

        .field {
            grid-template-columns: 1fr;
            gap: 5px;
        }

        .secret-type-tabs {
            flex-wrap: wrap;
        }

        .tab-btn {
            flex: 1;
            min-width: 100px;
        }
    }
</style>