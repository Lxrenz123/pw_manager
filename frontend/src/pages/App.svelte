<script>
    import { onMount } from "svelte";
    import { apiBase } from "../script/api-base-url";
    import { credentialSchema } from "../script/schema";
    import { userKey} from "../stores/user-key.js"
    import { get } from "svelte/store";
    import { navigate } from "svelte-routing";
    import { deriveKey } from "../script/crypto";

    let newNote = $state({});
    let newCredential = $state({});
    let newDocument = $state({});

    let userId = $state("");
    let userEmail = $state("");
    let userCreationDate = $state("");
    let userLastLogin = $state("");

    let user2FA = $state(false);

    let showProfileModal = $state(false);
    let showProfile = $state(false);

    let plaintext;

    let vaults = $state([]);
    let vaultName = $state("");

    let secrets = $state([]);
    
    let title = $state("");
    let data_plaintext = $state("");
    let data_encrypted = $state("");
    let selectedVaultId = $state(null); 

    let user;
    let newEmail = $state("");

    let showConfirmModal = $state(false);

    let username = $state("");
    let password = $state("");
    let url = $state("");
    let note = $state("");
    let doc = $state("")
    let selectedFile = $state(null);
    let fileName = $state("");
    let fileSize = $state(0);
    let fileType = $state("");
    let activeSecretType = $state("credential"); // Track which form is active
    let visiblePasswords = $state(new Set()); // Track which passwords are visible

    let newPW = $state("");
    let currentPW = $state("");
    let confirmPW = $state("");

    let emailUpdateSuccess = $state("");
    let passwordUpdateSuccess = $state("");
    
    let isGeneratingPassword = $state(false);
    let showPasswordInForm = $state(false);

    async function disable2FA(){

        const response = await fetch(`${apiBase}/2fa/disable`, {
        method: "POST",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({"code": mfaCode})
    });

        if (!response.ok){
            throw new Error("Error");
            return;
        }

        user2FA = false

        return "Successfully disabled 2FA"
    }
    function generateSecurePassword() {
        isGeneratingPassword = true;
        
     
        const lowercase = 'abcdefghijklmnopqrstuvwxyz';
        const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const numbers = '0123456789';
        const symbols = '!@#$%';
        
   
        const allCharacters = lowercase + uppercase + numbers + symbols;
        
     
        const passwordLength = 16;
        let generatedPassword = '';
        
     
        const requiredChars = [
            lowercase[Math.floor(Math.random() * lowercase.length)],
            uppercase[Math.floor(Math.random() * uppercase.length)],
            numbers[Math.floor(Math.random() * numbers.length)],
            symbols[Math.floor(Math.random() * symbols.length)]
        ];
        
   
        for (let i = requiredChars.length; i < passwordLength; i++) {
            requiredChars.push(allCharacters[Math.floor(Math.random() * allCharacters.length)]);
        }
        
       
        for (let i = requiredChars.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [requiredChars[i], requiredChars[j]] = [requiredChars[j], requiredChars[i]];
        }
        
        password = requiredChars.join('');
        
     
        setTimeout(() => {
            isGeneratingPassword = false;
        }, 300);
    }

    async function updateEmail(){
 
        const response = await fetch(`${apiBase}/user/email`, {
        method: "PATCH",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({"email": newEmail})
    });

        if (!response.ok){
            throw new Error("Error");
            return;
        }

        user = await response.json();

        emailUpdateSuccess = "Email updated successfully!";

        setTimeout(() => {
            emailUpdateSuccess = ""
        }, 3000);

        newEmail = "";
        profile();
        return user.email
    }

    let credentialPWlength = $state("");

    async function generatePassword(){

  

    }

    let b64_OldSalt;

    async function updatePassword(){

        const response = await fetch(`${apiBase}/user/salt`, {
        method: "GET",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
    });

        if (!response.ok){
            throw new Error("Error");
        }

        b64_OldSalt = await response.json()

        const bytesOldSalt = Uint8Array.from(atob(b64_OldSalt), c => c.charCodeAt(0));
        

        const { key: newDerivedKey } = await deriveKey(newPW, bytesOldSalt);

        const iv = crypto.getRandomValues(new Uint8Array(12));
        const userKeyBytes = await crypto.subtle.exportKey("raw", get(userKey))

        const encryptedUserKey = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv},
        newDerivedKey,
        userKeyBytes
        );



        

        const response1 = await fetch(`${apiBase}/user/password`, {
        method: "PATCH",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({"current_password": currentPW, "password": newPW, "user_key": btoa(String.fromCharCode(...new Uint8Array(encryptedUserKey))),
        iv: btoa(String.fromCharCode(...iv))
    })
    });

        if (!response1.ok){
            throw new Error("Error");

        }

        passwordUpdateSuccess = "Successfully updated your master password!"

        setTimeout(() =>
        {
            passwordUpdateSuccess = ""

        },3000);
        
        currentPW = "";
        newPW = "";
        confirmPW = "";


        return "Password successfully updated!"
    }


    function logout() {
        localStorage.removeItem("access_token");
        userKey.set(null);
        navigate("/login");
    }

    async function profile(){
        showProfile = true;

        const response = await fetch(`${apiBase}/user/me`, {
        method: "GET",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        }});

        if (!response.ok){
            throw new Error("Error");
            return;
        }

        user = await response.json();

        userId = user.id;
        userEmail = user.email;
        userCreationDate = user.created_at;
        userLastLogin = user.last_login;
        user2FA = user.mfa_enabled;


    }

    let mfaSetupData;
    let showMFASetup = $state(false);
    let otp_uri = $state("");
    let qrcodeb64 = $state("");

    async function mfaSetup(){
        showMFASetup = true

    const response = await fetch(`${apiBase}/2fa/setup`, {
        method: "POST",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        }});

        if (!response.ok){
            throw new Error("Error");
            return;
        }

        mfaSetupData = await response.json();

        otp_uri = mfaSetupData.otp_uri
        qrcodeb64 = mfaSetupData.qr_data_url


    }
    let mfaConfirm = $state("");
    let mfaCode = $state("");

    async function confirm2FA(){
            

    const response = await fetch(`${apiBase}/2fa/confirm`, {
        method: "POST",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({"code": mfaCode})

    });

        if (!response.ok){
            throw new Error("Error");
            return;
        }

        mfaConfirm = await response.json();
    

        user2FA = true;
        showMFASetup = false;

        return mfaConfirm
    }



    let confirmMasterPW = $state("");
    let secretId = $state("");
    let showDeleteSecretModal = $state(false);
    let secretToDelete = $state(null);

    function confirmDeleteSecret(id) {
        secretToDelete = secrets.find(s => s.id === id);
        secretId = id;
        showDeleteSecretModal = true;
    }

    function cancelDeleteSecret() {
        showDeleteSecretModal = false;
        secretToDelete = null;
        secretId = null;
    }

    async function deleteSecret(){
        try {
            const response = await fetch(`${apiBase}/secret/${secretId}`, {
                method: "DELETE",
                headers: {
                'Content-Type': 'application/json',
                'accept': "application/json",
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                }, 
            });

            if (!response.ok){
                throw new Error("Failed to delete secret");
            }

            // Remove the secret from the local array
            secrets = secrets.filter(s => s.id !== secretId);
            
            // Close modal and reset state
            showDeleteSecretModal = false;
            secretToDelete = null;
            secretId = null;

        } catch (error) {
            console.error("Error deleting secret:", error);
            alert("Failed to delete secret. Please try again.");
        }
    }

let showEditSecretModal = $state(false);
let secretToEdit = $state(null);
let editedSecretData = $state({});
let isEditingSecret = $state(false);

// Add this function to open the edit modal
function openEditSecret(secret) {
    secretToEdit = secret;
    // Clone the secret data for editing
    editedSecretData = JSON.parse(JSON.stringify(secret.data));
    showEditSecretModal = true;
}

function cancelEditSecret() {
    showEditSecretModal = false;
    secretToEdit = null;
    editedSecretData = {};
}
  async function updateSecret() {
    if (!secretToEdit || !editedSecretData) return;
    
    try {
        isEditingSecret = true;

        // Generate new encryption for the updated data
        const secretKeyBytes = crypto.getRandomValues(new Uint8Array(32));
        const secretKey = await crypto.subtle.importKey(
            "raw",
            secretKeyBytes,
            { name: "AES-GCM" },
            true,
            ["encrypt", "decrypt"]
        );

        const encoder = new TextEncoder();
        const plaintext = encoder.encode(JSON.stringify(editedSecretData));
        const secretIv = crypto.getRandomValues(new Uint8Array(12));

        const encryptedSecret = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv: secretIv },
            secretKey,
            plaintext
        );

        const userKeyValue = get(userKey);
        if (!userKeyValue || !(userKeyValue instanceof CryptoKey)) {
            localStorage.removeItem("access_token");
            navigate("/login");
            return;
        }

        const secretKeyIv = crypto.getRandomValues(new Uint8Array(12));
        const encryptedSecretKey = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv: secretKeyIv },
            userKeyValue,
            secretKeyBytes
        );

        // Convert to base64
        function arrayBufferToBase64(buffer) {
            const bytes = new Uint8Array(buffer);
            let binary = '';
            for (let i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
        }

        const encryptedSecretB64 = arrayBufferToBase64(encryptedSecret);
        const secretIvB64 = arrayBufferToBase64(secretIv);
        const encryptedSecretKeyB64 = arrayBufferToBase64(encryptedSecretKey);
        const secretKeyIvB64 = arrayBufferToBase64(secretKeyIv);

        const response = await fetch(`${apiBase}/secret/${secretToEdit.id}`, {
            method: "PATCH",
            headers: {
                'Content-Type': 'application/json',
                'accept': "application/json",
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`
            },
            body: JSON.stringify({
                data_encrypted: encryptedSecretB64,
                secret_iv: secretIvB64,
                encrypted_secret_key: encryptedSecretKeyB64,
                secret_key_iv: secretKeyIvB64
            })
        });

        if (!response.ok) {
            throw new Error("Failed to update secret");
        }

        // Update the secret in the local array
        const secretIndex = secrets.findIndex(s => s.id === secretToEdit.id);
        if (secretIndex !== -1) {
            secrets[secretIndex] = {
                ...secrets[secretIndex],
                data: editedSecretData
            };
        }

        // Close modal and reset state
        showEditSecretModal = false;
        secretToEdit = null;
        editedSecretData = {};

    } catch (error) {
        console.error("Error updating secret:", error);
        alert("Failed to update secret. Please try again.");
    } finally {
        isEditingSecret = false;
    }
}

    async function deleteMe(){

        showConfirmModal = true

        }
    
        async function confirmDelete() {
            

        const response = await fetch(`${apiBase}/user`, {
        method: "DELETE",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({"password": confirmMasterPW})
    
    });

        if (!response.ok){
            throw new Error("Error");
            return;
        }

        localStorage.removeItem("access_token");
        userKey.set(null);

        navigate("/");
    }

    function cancelDelete(){
        showConfirmModal = false;
        confirmMasterPW = "";
    }

    async function secretsExport(){

        const response = await fetch(`${apiBase}/secret`, {
        method: "GET",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        }});

        if (!response.ok){
            throw new Error("Error");
            return;
        }

        const secrets = await response.json();



    }


    function handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            // File size limit: 10MB
            const maxSize = 10 * 1024 * 1024; // 10MB in bytes
            if (file.size > maxSize) {
                alert("File size must be less than 10MB");
                event.target.value = "";
                return;
            }

            // Allowed file types
            const allowedTypes = [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'image/gif',
                'text/plain',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ];

            if (!allowedTypes.includes(file.type)) {
                alert("File type not supported. Please upload PDF, images, or text documents.");
                event.target.value = "";
                return;
            }

            selectedFile = file;
            fileName = file.name;
            fileSize = file.size;
            fileType = file.type;
        }
    }

    async function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                // Remove the data URL prefix (data:*/*;base64,)
                const result = reader.result;
                if (typeof result === 'string') {
                    const base64 = result.split(',')[1];
                    resolve(base64);
                } else {
                    reject(new Error('Expected string result from FileReader'));
                }
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    function downloadFile(fileData) {
        try {
            // Convert base64 back to blob
            const byteCharacters = atob(fileData.fileData);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: fileData.fileType });
            
            // Create download link
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = fileData.fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            alert('Error downloading file: ' + error.message);
        }
    }

    async function copyToClipboard(text, fieldName) {
        try {
            await navigator.clipboard.writeText(text);
            // Show temporary feedback
            const originalFieldName = fieldName;
            // You could add a toast notification here if desired
            console.log(`${originalFieldName} copied to clipboard`);
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            console.log(`${fieldName} copied to clipboard (fallback)`);
        }
    }

    function togglePasswordVisibility(secretId) {
        if (visiblePasswords.has(secretId)) {
            visiblePasswords.delete(secretId);
        } else {
            visiblePasswords.add(secretId);
        }
        // Trigger reactivity
        visiblePasswords = new Set(visiblePasswords);
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
        return;
    }

    // Auto-select the first vault if no vault is currently selected and vaults exist
    if (!selectedVaultId && vaults.length > 0) {
        selectedVaultId = vaults[0].id;
        getSecretsOfVault(vaults[0].id);
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
        return;
    }

    const newVault = await response.json()
    vaults.push(newVault)
    vaultName = "";

    // Auto-select the newly created vault
    selectedVaultId = newVault.id;
    getSecretsOfVault(newVault.id);

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
        return;
    }
    const encryptedSecrets = await response.json(); 
    selectedVaultId = vaultId;
    showProfile = false; // Hide profile when vault is selected



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
            localStorage.removeItem("access_token");
            navigate("/login");
            return { ...secret, data: null };

        }
    }));

    
}


async function addSecret(secret_type){
    console.log("addSecret called with:", secret_type);
    
    // Add a simple check to prevent infinite recursion
    if (addSecret._running) {
        console.warn("addSecret already running, preventing recursion");
        return;
    }
    addSecret._running = true;

    try {
        newCredential = {
            title: title,
            username: username,
            password: password,
            url: url,
            note: note
        }
        newNote = {
            title: title,
            content: note
        }

        if (secret_type === "document") {
            if (!selectedFile) {
                alert("Please select a file to upload");
                return;
            }
            
            // Add file size limit (5MB)
            if (selectedFile.size > 5 * 1024 * 1024) {
                alert("File too large. Maximum size is 5MB.");
                return;
            }
            
            try {
                const fileBase64 = await fileToBase64(selectedFile);
                newDocument = {
                    title: title,
                    fileName: fileName,
                    fileType: fileType,
                    fileSize: fileSize,
                    fileData: fileBase64
                };
            } catch (error) {
                alert("Error reading file: " + error.message);
                return;
            }
        } else {
            newDocument = {
                file: doc
            };
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
            localStorage.removeItem("access_token");
            navigate("/login")
        }

    const secretKeyIv = crypto.getRandomValues(new Uint8Array(12));

    const encryptedSecretKey = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: secretKeyIv },
    userKeyValue,
    secretKeyBytes
    )

    // Use a safer approach for large data to avoid stack overflow
    function arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    const encryptedSecretB64 = arrayBufferToBase64(encryptedSecret);
    const secretIvB64 = arrayBufferToBase64(secretIv);
    const encryptedSecretKeyB64 = arrayBufferToBase64(encryptedSecretKey);
    const secretKeyIvB64 = arrayBufferToBase64(secretKeyIv);



    const response = await fetch(`${apiBase}/secret/${selectedVaultId}/${secret_type}`, {
        method: "POST",
        headers: {
        'Content-Type': 'application/json',
        'accept': "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({            
            data_encrypted: encryptedSecretB64,
            secret_iv: secretIvB64,
            encrypted_secret_key: encryptedSecretKeyB64,
            secret_key_iv: secretKeyIvB64})
    })

    if (!response.ok){
        throw new Error("Network error");
        return;
    }

    const newSecret = await response.json()
    
            

    const decryptedData = secret_type == "note" ? newNote : 
                            secret_type == "credential" ? newCredential : newDocument;
    

    secrets.push({ ...newSecret, data: decryptedData });
            

    // Clear form fields based on secret type
title = "";
        note = "";

        username = "";
        password = "";
        url = "";
        note = "";

        doc = "";
        selectedFile = null;
        fileName = "";
        fileSize = 0;
        fileType = "";

        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput instanceof HTMLInputElement) fileInput.value = "";
    
        title = "";
    
    } catch (error) {
        console.error("Error in addSecret:", error);
        alert("Error adding secret: " + error.message);
    } finally {
        addSecret._running = false;
    }
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
            <button class="profile-btn" class:active={showProfile} onclick={profile}>
                <span>profile</span>
                <span class="profile-icon">⏻</span>
            </button>
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
                <input 
                    class="vault-input" 
                    placeholder="vault_name" 
                    bind:value={vaultName} 
                />
                <button class="add-vault-btn" onclick={addVault} disabled={vaultName == ""}>
                    <span>CREATE</span>
                </button>
            </div>

            <!-- Add Secret Section -->
            <div class="add-secret-sidebar">
                <div class="sidebar-header">
                    <h3 class="sidebar-title">// ADD SECRET</h3>
                </div>
                    
                    <!-- Secret Type Dropdown -->
                    <div class="sidebar-dropdown-section">
                        <label class="dropdown-label">secret_type:</label>
                        <select 
                            class="sidebar-dropdown"
                            bind:value={activeSecretType}
                        >
                            <option value="credential">🔑 CREDENTIAL</option>
                            <option value="note">📝 NOTE</option>
                            <option value="document">📄 DOCUMENT</option>
                        </select>
                    </div>

                    <!-- Forms -->
                    <div class="sidebar-form">
                        {#if activeSecretType === "credential"}
                            <input 
                                placeholder="secret_title" 
                                class="sidebar-input" 
                                bind:value={title} 
                            />
                            <input 
                                placeholder="username" 
                                class="sidebar-input" 
                                bind:value={username} 
                            />
                            <div class="password-input-section">
                                <input 
                                    placeholder="password" 
                                    type={showPasswordInForm ? 'text' : 'password'}
                                    class="sidebar-input" 
                                    bind:value={password} 
                                />
                                <div class="password-buttons">
                                    <button 
                                        class="generate-password-btn" 
                                        onclick={generateSecurePassword}
                                        disabled={isGeneratingPassword}
                                        title="Generate secure password"
                                    >
                                        <span class="generate-icon">{isGeneratingPassword ? '⏳' : '🎲'}</span>
                                        <span class="button-text">GENERATE</span>
                                    </button>
                                    <button 
                                        class="toggle-password-btn" 
                                        onclick={() => showPasswordInForm = !showPasswordInForm}
                                        title={showPasswordInForm ? 'Hide password' : 'Show password'}
                                    >
                                        <span class="toggle-icon">{showPasswordInForm ? '🙈' : '👁️'}</span>
                                        <span class="button-text">{showPasswordInForm ? 'HIDE' : 'SHOW'}</span>
                                    </button>
                                    <button 
                                        class="copy-password-btn" 
                                        onclick={() => copyToClipboard(password, 'Password')}
                                        disabled={!password}
                                        title="Copy password to clipboard"
                                    >
                                        <span class="copy-icon">📋</span>
                                        <span class="button-text">COPY</span>
                                    </button>
                                </div>
                            </div>
                     
                            <textarea 
                                placeholder="additional_notes (optional)" 
                                class="sidebar-textarea" 
                                bind:value={note}
                                rows="2"
                            ></textarea>
                            <button 
                                class="sidebar-add-btn" 
                                class:disabled={!selectedVaultId}
                                disabled={!selectedVaultId || title == ""} 
                                onclick={() => selectedVaultId && addSecret("credential")}
                            >>
                                <span>ENCRYPT & STORE</span>
                                <span class="btn-icon">🔐</span>
                            </button>
                        {:else if activeSecretType === "note"}
                            <input 
                                placeholder="secret_title" 
                                class="sidebar-input" 
                                bind:value={title} 
                            />
                            <textarea 
                                placeholder="note_content" 
                                class="sidebar-textarea" 
                                bind:value={note}
                                rows="3"
                            ></textarea>
                            <button 
                                class="sidebar-add-btn" 
                                class:disabled={!selectedVaultId}
                                disabled={!selectedVaultId || title == ""}
                                onclick={() => selectedVaultId && addSecret("note")}
                            >>
                                <span>ENCRYPT & STORE</span>
                                <span class="btn-icon">🔐</span>
                            </button>
                        {:else if activeSecretType === "document"}
                            <input 
                                placeholder="document_title" 
                                class="sidebar-input" 
                                bind:value={title} 
                            />
                            <label class="sidebar-file-upload">
                                <input 
                                    type="file" 
                                    class="file-input"
                                    accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif"
                                    onchange={handleFileUpload}
                                />
                                <span class="file-upload-text">
                                    {#if selectedFile}
                                        📄 {fileName}
                                    {:else}
                                        📎 Upload file
                                    {/if}
                                </span>
                            </label>
                            {#if selectedFile}
                                <div class="sidebar-file-info">
                                    <span class="file-detail">Size: {(fileSize / 1024).toFixed(1)} KB</span>
                                </div>
                            {/if}
                            <textarea 
                                placeholder="description (optional)" 
                                class="sidebar-textarea" 
                                bind:value={doc}
                                rows="2"
                            ></textarea>
                            <button 
                                class="sidebar-add-btn" 
                                class:disabled={!selectedVaultId}
                                disabled={!selectedVaultId || title == ""}
                                onclick={() => selectedVaultId && addSecret("document")}
                            >
                                <span>ENCRYPT & STORE</span>
                                <span class="btn-icon">🔐</span>
                            </button>
                        {/if}
                    </div>
                </div>
        </aside>

        <!-- Secrets Content -->
        <section class="secrets-content">
            {#if showProfile}
                <!-- Profile Content -->
                <div class="profile-content">
                    <div class="profile-header">
                        <h2 class="section-title">// USER PROFILE SETTINGS</h2>
                        <div class="profile-status">
                            <span class="status-indicator">●</span>
                            <span>PROFILE ACTIVE</span>
                        </div>
                    </div>

                    <div class="profile-sections">
                        <div class="profile-section">
                            <h3 class="section-header">$ account_info --current</h3>
                            <div class="info-grid">
                                <div class="info-item">
                                    <span class="info-label">user_id:</span>
                                    <span class="info-value">{userId}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">email:</span>
                                    <span class="info-value">{userEmail}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">created:</span>
                                    <span class="info-value">{userCreationDate}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">last_login:</span>
                                    <span class="info-value">{userLastLogin}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">2 Factor Authentication</span>
                                    <span class="info-value">{String(user2FA)}</span>
                                </div>
                            </div>
                        </div>

                        {#if !user2FA}
                        <div class="profile-section">
                            <h3 class="section-header">$ enable_2fa --security</h3>
                            <div class="security-info">
                                <div class="security-description">
                                    <span class="security-icon">🔐</span>
                                    <div class="security-text">
                                        <h4>Two-Factor Authentication</h4>
                                        <p>Add an extra layer of security to your account with TOTP-based 2FA</p>
                                    </div>
                                </div>
                                <button class="profile-action-btn primary" onclick={mfaSetup}>
                                    <span>ENABLE 2FA</span>
                                    <span class="btn-icon">🛡️</span>
                                </button>
                            </div>
                        </div>
                        {/if}

                        <div class="profile-section">
                            <h3 class="section-header">$ update_email --new</h3>
                            
                         {#if emailUpdateSuccess}
                            <div class="success-message">
                                <span class="success-icon">✓</span>
                                <span class="success-text">{emailUpdateSuccess}</span>
                            </div>
                        {/if}
                            <div class="form-group">
                                <label class="form-label">current_email:</label>
                                <input 
                                    type="email" 
                                    class="profile-input" 
                                    value={userEmail}
                                    disabled
                                />
                            </div>
                            <div class="form-group">
                                <label class="form-label">new_email:</label>
                                <input 
                                    type="email" 
                                    class="profile-input" 
                                    placeholder="new.email@domain.com"
                                    bind:value={newEmail}
                                />
                            </div>
                
                            <button class="profile-action-btn primary" onclick={updateEmail}>
                                <span>UPDATE EMAIL</span>
                                <span class="btn-icon">📧</span>
                            </button>
                        </div>

                        <div class="profile-section">
                            <h3 class="section-header">$ change_password --master</h3>
                        {#if passwordUpdateSuccess}
                            <div class="success-message">
                                <span class="success-icon">✓</span>
                                <span class="success-text">{passwordUpdateSuccess}</span>
                            </div>
                        {/if}
                
                            <div class="form-group">
                                <label class="form-label">current_password:</label>
                                <input 
                                    bind:value={currentPW}
                                    type="password" 
                                    class="profile-input" 
                                    placeholder="enter current master password"
                                />
                            </div>
                            <div class="form-group">
                                <label class="form-label">new_password:</label>
                                <input
                                    bind:value={newPW}
                                    type="password" 
                                    class="profile-input" 
                                    placeholder="enter new master password"
                                />
                            </div>
                            <div class="form-group">
                                <label class="form-label">confirm_password:</label>
                                <input 
                                    bind:value={confirmPW}
                                    type="password" 
                                    class="profile-input" 
                                    placeholder="confirm new master password"
                                />
                            </div>
                            <button class="profile-action-btn danger" disabled={newPW !== confirmPW || newPW == "" || confirmPW == "" || confirmPW.length < 8 || newPW.length < 8} onclick={updatePassword}>
                                <span>CHANGE PASSWORD</span>
                                <span class="btn-icon">🔐</span>
                            </button>
                        </div>

                        <div class="profile-section">
                            <h3 class="section-header">$ security_actions --danger</h3>
                            <div class="danger-zone">
                                <div class="danger-item">
                                    <div class="danger-info">
                                        <h4>Export Encrypted Data</h4>
                                        <p>Download all your encrypted vault data for backup purposes</p>
                                    </div>
                                    <button class="profile-action-btn secondary">
                                        <span>EXPORT DATA</span>
                                        <span class="btn-icon">📤</span>
                                    </button>
                                </div>
                                <div class="danger-item">
                                    <div class="danger-info">
                                        <h4>Delete Account</h4>
                                        <p>Permanently delete your account and all associated data</p>
                                    </div>
                                    <button class="profile-action-btn danger" onclick={deleteMe}>
                                        <span>DELETE ACCOUNT</span>
                                        <span class="btn-icon">🗑️</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            {:else if selectedVaultId}
                <div class="secrets-header">
                    <h2 class="section-title">// ENCRYPTED SECRETS</h2>
                    <div class="vault-status">
                        <span class="status-indicator">●</span>
                        <span>VAULT DECRYPTED</span>
                    </div>
                </div>

                <!-- Secrets List -->
                <div class="secrets-list">
                    {#each secrets as secret}
                        <div class="secret-card">
                            <div class="secret-header">
                                <h4 class="secret-title">{secret.data?.title}</h4>
                                <div class="secret-meta">
                                    <span class="secret-type">
                                        {#if secret.data?.content}
                                            NOTE
                                        {:else if secret.data?.username}
                                            CREDENTIAL
                                        {:else if secret.data?.fileName || secret.data?.file}
                                            DOCUMENT
                                        {:else}
                                            DATA
                                        {/if}
                                    </span>
                                    <div class="secret-actions">
                                        <button class="secret-action-btn update-btn" onclick={() => openEditSecret(secret)}>
                                            <span class="update-icon">🖊️</span>
                                        </button>
                                        <button class="secret-action-btn delete-btn" onclick={() => confirmDeleteSecret(secret.id)}>
                                            <span class="delete-icon">🗑️</span>
                                        </button>
                                
                                    </div>

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
                                        <div class="field credential-field">
                                            <span class="field-label">username:</span>
                                            <div class="field-value-with-actions">
                                                <span class="field-value">{secret.data.username}</span>
                                                <button class="copy-btn" onclick={() => copyToClipboard(secret.data.username, 'Username')}>
                                                    <span>📋</span>
                                                </button>
                                            </div>
                                        </div>
                                        <div class="field credential-field">
                                            <span class="field-label">password:</span>
                                            <div class="field-value-with-actions">
                                                <span class="field-value password">
                                                    {visiblePasswords.has(secret.id) ? secret.data.password : "•".repeat(secret.data.password.length)}
                                                </span>
                                                <div class="password-actions">
                                                    <button class="toggle-btn" onclick={() => togglePasswordVisibility(secret.id)}>
                                                        <span>{visiblePasswords.has(secret.id) ? '🙈' : '👁️'}</span>
                                                    </button>
                                                    <button class="copy-btn" onclick={() => copyToClipboard(secret.data.password, 'Password')}>
                                                        <span>📋</span>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                        {#if secret.data.url}
                                            <div class="field credential-field">
                                                <span class="field-label">url:</span>
                                                <div class="field-value-with-actions">
                                                    <span class="field-value">{secret.data.url}</span>
                                                    <button class="copy-btn" onclick={() => copyToClipboard(secret.data.url, 'URL')}>
                                                        <span>📋</span>
                                                    </button>
                                                </div>
                                            </div>
                                        {/if}
                                        {#if secret.data.note}
                                            <div class="field">
                                                <span class="field-label">note:</span>
                                                <span class="field-value">{secret.data.note}</span>
                                            </div>
                                        {/if}
                                    {:else if secret.data.fileName}
                                        <!-- New file upload format -->
                                        <div class="field">
                                            <span class="field-label">file:</span>
                                            <span class="field-value file-name">{secret.data.fileName}</span>
                                        </div>
                                        <div class="field">
                                            <span class="field-label">type:</span>
                                            <span class="field-value">{secret.data.fileType}</span>
                                        </div>
                                        <div class="field">
                                            <span class="field-label">size:</span>
                                            <span class="field-value">{(secret.data.fileSize / 1024).toFixed(1)} KB</span>
                                        </div>
                                        <div class="field file-actions">
                                            <span class="field-label">actions:</span>
                                            <div class="action-buttons">
                                                <button class="action-btn download-btn" onclick={() => downloadFile(secret.data)}>
                                                    <span>📥 Download</span>
                                                </button>
                                            </div>
                                        </div>
                                    {:else if secret.data.file}
                                        <!-- Legacy text format -->
                                        <div class="field">
                                            <span class="field-label">content:</span>
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
                    <p>Choose a vault from the sidebar to decrypt and view your secrets, or use the profile button to manage your account</p>
                </div>
            {/if}
        </section>
    </main>
<!-- Add this after the MFA Setup Modal -->
<!-- Edit Secret Modal -->
{#if showEditSecretModal && secretToEdit}
    <div class="modal-overlay" onclick={cancelEditSecret}>
        <div class="modal-container edit-modal" onclick={(e) => e.stopPropagation()}>
            <div class="modal-header">
                <h2 class="modal-title">
                    <span class="modal-icon">✏️</span>
                    <span>Edit Secret</span>
                </h2>
                <button class="modal-close" onclick={cancelEditSecret}>
                    ×
                </button>
            </div>
            
            <div class="modal-body">
                <div class="edit-content">
                    <div class="edit-form">
                        {#if editedSecretData.username !== undefined}
                            <!-- Credential Form -->
                            <div class="form-section">
                                <h3 class="form-section-title">$ edit_credential --update</h3>
                                <div class="form-group">
                                    <label class="form-label">title:</label>
                                    <input 
                                        type="text" 
                                        class="edit-input" 
                                        bind:value={editedSecretData.title}
                                        placeholder="Secret title"
                                    />
                                </div>
                                <div class="form-group">
                                    <label class="form-label">username:</label>
                                    <input 
                                        type="text" 
                                        class="edit-input" 
                                        bind:value={editedSecretData.username}
                                        placeholder="Username"
                                    />
                                </div>
                                <div class="form-group">
                                    <label class="form-label">password:</label>
                                    <input 
                                        type="password" 
                                        class="edit-input" 
                                        bind:value={editedSecretData.password}
                                        placeholder="Password"
                                    />
                                </div>
                                <div class="form-group">
                                    <label class="form-label">url:</label>
                                    <input 
                                        type="url" 
                                        class="edit-input" 
                                        bind:value={editedSecretData.url}
                                        placeholder="Website URL (optional)"
                                    />
                                </div>
                                <div class="form-group">
                                    <label class="form-label">notes:</label>
                                    <textarea 
                                        class="edit-textarea" 
                                        bind:value={editedSecretData.note}
                                        placeholder="Additional notes (optional)"
                                        rows="3"
                                    ></textarea>
                                </div>
                            </div>
                        {:else if editedSecretData.content !== undefined}
                            <!-- Note Form -->
                            <div class="form-section">
                                <h3 class="form-section-title">$ edit_note --update</h3>
                                <div class="form-group">
                                    <label class="form-label">title:</label>
                                    <input 
                                        type="text" 
                                        class="edit-input" 
                                        bind:value={editedSecretData.title}
                                        placeholder="Note title"
                                    />
                                </div>
                                <div class="form-group">
                                    <label class="form-label">content:</label>
                                    <textarea 
                                        class="edit-textarea" 
                                        bind:value={editedSecretData.content}
                                        placeholder="Note content"
                                        rows="6"
                                    ></textarea>
                                </div>
                            </div>
                        {:else if editedSecretData.fileName !== undefined || editedSecretData.file !== undefined}
                            <!-- Document Form -->
                            <div class="form-section">
                                <h3 class="form-section-title">$ edit_document --update</h3>
                                <div class="form-group">
                                    <label class="form-label">title:</label>
                                    <input 
                                        type="text" 
                                        class="edit-input" 
                                        bind:value={editedSecretData.title}
                                        placeholder="Document title"
                                    />
                                </div>
                                {#if editedSecretData.fileName}
                                    <div class="current-file-info">
                                        <div class="file-info-header">
                                            <span class="file-icon">📄</span>
                                            <span class="current-file-label">Current file:</span>
                                        </div>
                                        <div class="file-details">
                                            <div class="file-detail">
                                                <span class="detail-label">name:</span>
                                                <span class="detail-value">{editedSecretData.fileName}</span>
                                            </div>
                                            <div class="file-detail">
                                                <span class="detail-label">type:</span>
                                                <span class="detail-value">{editedSecretData.fileType}</span>
                                            </div>
                                            <div class="file-detail">
                                                <span class="detail-label">size:</span>
                                                <span class="detail-value">{(editedSecretData.fileSize / 1024).toFixed(1)} KB</span>
                                            </div>
                                        </div>
                                        <div class="file-actions">
                                            <button class="file-action-btn" onclick={() => downloadFile(editedSecretData)}>
                                                <span>📥 Download Current</span>
                                            </button>
                                        </div>
                                        <div class="file-note">
                                            <span class="note-icon">ℹ️</span>
                                            <span class="note-text">Note: File content cannot be edited. Only title and description can be updated.</span>
                                        </div>
                                    </div>
                                {:else}
                                    <div class="form-group">
                                        <label class="form-label">description:</label>
                                        <textarea 
                                            class="edit-textarea" 
                                            bind:value={editedSecretData.file}
                                            placeholder="Document description"
                                            rows="4"
                                        ></textarea>
                                    </div>
                                {/if}
                            </div>
                        {/if}
                        
                        <div class="edit-actions">
                            <button class="edit-btn cancel" onclick={cancelEditSecret}>
                                <span>CANCEL</span>
                                <span class="btn-icon">↩️</span>
                            </button>
                            <button 
                                class="edit-btn save" 
                                onclick={updateSecret}
                                disabled={isEditingSecret}
                            >
                                <span>{isEditingSecret ? 'UPDATING...' : 'SAVE CHANGES'}</span>
                                <span class="btn-icon">{isEditingSecret ? '⏳' : '💾'}</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}
<!-- Replace the existing showConfirmModal section -->
{#if showConfirmModal}
    <div class="modal-overlay" onclick={cancelDelete}>
        <div class="modal-container confirm-modal" onclick={(e) => e.stopPropagation()}>
            <div class="modal-header">
                <h2 class="modal-title">
                    <span class="modal-icon">⚠️</span>
                    <span>Delete Account Confirmation</span>
                </h2>
                <button class="modal-close" onclick={cancelDelete}>
                    ×
                </button>
            </div>
            
            <div class="modal-body">
                <div class="warning-content">
                    <div class="warning-message">
                        <span class="warning-icon">🚨</span>
                        <div class="warning-text">
                            <h3>This action cannot be undone!</h3>
                            <p>Deleting your account will permanently remove:</p>
                            <ul>
                                <li>All your encrypted vaults and secrets</li>
                                <li>Your user profile and settings</li>
                                <li>Your 2FA configuration</li>
                                <li>All backup recovery options</li>
                            </ul>
                            <p><strong>Are you absolutely sure you want to delete your account?</strong></p>
                        </div>
                    </div>
                         <div class="password-confirmation">
                        <div class="form-group">
                            <label class="form-label">master_password:</label>
                            <input 
                                type="password" 
                                class="profile-input password-confirm-input" 
                                placeholder="enter your master password"
                                bind:value={confirmMasterPW}
                                autocomplete="current-password"
                            />
                        </div>
                    </div>
                    <div class="confirm-actions">
                        <button class="confirm-btn cancel" onclick={cancelDelete}>
                            <span>CANCEL</span>
                            <span class="btn-icon">↩️</span>
                        </button>
                        <button class="confirm-btn delete" onclick={confirmDelete}>
                            <span>DELETE ACCOUNT</span>
                            <span class="btn-icon">🗑️</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}

    <!-- Delete Secret Confirmation Modal -->
    {#if showDeleteSecretModal}
        <div class="modal-overlay" onclick={cancelDeleteSecret}>
            <div class="modal-container confirm-modal" onclick={(e) => e.stopPropagation()}>
                <div class="modal-header">
                    <h2 class="modal-title">
                        <span class="modal-icon">🗑️</span>
                        <span>Delete Secret</span>
                    </h2>
                    <button class="modal-close" onclick={cancelDeleteSecret}>
                        ×
                    </button>
                </div>
                
                <div class="modal-body">
                    <div class="warning-content">
                        <div class="warning-message">
                            <span class="warning-icon">⚠️</span>
                            <div class="warning-text">
                                <h3>Are you sure you want to delete this secret?</h3>
                                <p><strong>Secret:</strong> {secretToDelete?.data?.title || 'Unknown'}</p>
                                <p><strong>Type:</strong> 
                                    {#if secretToDelete?.data?.content}
                                        Note
                                    {:else if secretToDelete?.data?.username}
                                        Credential
                                    {:else if secretToDelete?.data?.fileName || secretToDelete?.data?.file}
                                        Document
                                    {:else}
                                        Data
                                    {/if}
                                </p>
                                <p>This action cannot be undone. The secret will be permanently deleted from your vault.</p>
                            </div>
                        </div>
                        
                        <div class="confirm-actions">
                            <button class="confirm-btn cancel" onclick={cancelDeleteSecret}>
                                <span>CANCEL</span>
                                <span class="btn-icon">↩️</span>
                            </button>
                            <button class="confirm-btn delete" onclick={deleteSecret}>
                                <span>DELETE SECRET</span>
                                <span class="btn-icon">🗑️</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {/if}

    <!-- MFA Setup Modal -->
    {#if showMFASetup}
        <div class="modal-overlay" onclick={() => showMFASetup = false}>
            <div class="modal-container mfa-modal" onclick={(e) => e.stopPropagation()}>
                <div class="modal-header">
                    <h2 class="modal-title">
                        <span class="modal-icon">🔐</span>
                        <span>Two-Factor Authentication Setup</span>
                    </h2>
                    <button class="modal-close" onclick={() => showMFASetup = false}>
                        ×
                    </button>
                </div>
                
                <div class="modal-body">
                    <div class="mfa-setup-content">
                        <!-- Instructions Section -->
                        <div class="mfa-instructions">
                            <h3 class="instruction-title">$ setup_2fa --instructions</h3>
                            <div class="instruction-steps">
                                <div class="step">
                                    <span class="step-number">1.</span>
                                    <div class="step-content">
                                        <h4>Install Authenticator App</h4>
                                        <p>Download an authenticator app such as:</p>
                                        <ul>
                                            <li>Google Authenticator</li>
                                            <li>Authy</li>
                                            <li>Microsoft Authenticator</li>
                                            <li>1Password</li>
                                        </ul>
                                    </div>
                                </div>
                                
                                <div class="step">
                                    <span class="step-number">2.</span>
                                    <div class="step-content">
                                        <h4>Scan QR Code</h4>
                                        <p>Open your authenticator app and scan the QR code shown on the right, or manually enter the secret key below.</p>
                                    </div>
                                </div>
                                
                                <div class="step">
                                    <span class="step-number">3.</span>
                                    <div class="step-content">
                                        <h4>Verify Setup</h4>
                                        <p>Enter the 6-digit code from your authenticator app to complete the setup.</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="security-note">
                                <span class="warning-icon">⚠️</span>
                                <div class="note-content">
                                    <strong>Important:</strong> Save your secret key in a secure location. If you lose access to your authenticator app, you'll need this key to recover your account.
                                </div>
                            </div>
                        </div>
                        
                        <!-- QR Code Section -->
                        <div class="mfa-qr-section">
                            <div class="qr-container">
                                <h3 class="qr-title">$ scan_qr_code</h3>
                                {#if qrcodeb64}
                                    <div class="qr-code-wrapper">
                                        <img src={qrcodeb64} alt="2FA QR Code" class="qr-code" />
                                    </div>
                                {:else}
                                    <div class="qr-loading">
                                        <span>Generating QR Code...</span>
                                    </div>
                                {/if}
                                
                                <div class="manual-entry">
                                    <h4>Manual Entry</h4>
                                    <div class="secret-key-container">
                                        <label class="secret-label">Secret Key:</label>
                                        <div class="secret-value-container">
                                            <code class="secret-key">{otp_uri}</code>
                                            <button class="copy-btn" onclick={() => copyToClipboard(otp_uri, 'Secret Key')}>
                                                <span>📋</span>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="verification-section">
                                <h4>Verify Setup</h4>
                                <div class="verification-form">
                                    <input 
                                        type="text" 
                                        class="verification-input" 
                                        placeholder="Enter 6-digit code"
                                        maxlength="6"
                                        bind:value={mfaCode}
                                    />
                                    <button class="verify-btn" onclick={confirm2FA}>
                                        <span>VERIFY & ENABLE</span>
                                        <span class="btn-icon">✓</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {/if}
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
/* ...existing styles... */

.success-message {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 255, 65, 0.1);
    border: 1px solid rgba(0, 255, 65, 0.3);
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 0.8rem;
    margin-bottom: 15px;
    animation: slideInSuccess 0.3s ease;
}

@keyframes slideInSuccess {
    from {
        transform: translateY(-10px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.success-message .success-icon {
    color: #00ff41;
    font-size: 1rem;
    flex-shrink: 0;
    font-weight: bold;
}

.success-message .success-text {
    color: #00ff41;
    line-height: 1.3;
    font-weight: 500;
}

/* Add fade out animation */
.success-message.fade-out {
    animation: fadeOutSuccess 0.3s ease forwards;
}

@keyframes fadeOutSuccess {
    from {
        opacity: 1;
        transform: translateY(0);
    }
    to {
        opacity: 0;
        transform: translateY(-10px);
    }
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

    .profile-btn {
        background: rgba(0, 170, 255, 0.1);
        border: 1px solid #00aaff;
        color: #00aaff;
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

    .profile-btn:hover {
        background: rgba(0, 170, 255, 0.2);
        transform: translateY(-1px);
    }

    .profile-btn.active {
        background: rgba(0, 170, 255, 0.3);
        border-color: #00aaff;
        box-shadow: 0 0 15px rgba(0, 170, 255, 0.4);
    }

    .profile-icon {
        font-size: 1rem;
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
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .vault-input {
        width: 100%;
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #333;
        color: #00ff41;
        padding: 10px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        box-sizing: border-box;
    }

    .vault-input:focus {
        outline: none;
        border-color: #00ff41;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    }

    .add-vault-btn {
        width: 100%;
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
        box-sizing: border-box;
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

    /* File Upload Styles */
    .file-upload-section {
        display: grid;
        gap: 10px;
    }

    .file-upload-label {
        display: block;
        background: rgba(0, 0, 0, 0.8);
        border: 2px dashed #333;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'JetBrains Mono', monospace;
    }

    .file-upload-label:hover {
        border-color: #00aaff;
        background: rgba(0, 170, 255, 0.05);
        transform: translateY(-1px);
    }

    .file-input {
        display: none;
    }

    .file-upload-text {
        color: #00aaff;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .file-info {
        display: flex;
        justify-content: space-between;
        padding: 8px 12px;
        background: rgba(0, 170, 255, 0.1);
        border: 1px solid #00aaff;
        border-radius: 5px;
        font-size: 0.8rem;
    }

    .file-detail {
        color: #00aaff;
    }

    .file-name {
        color: #00aaff !important;
        font-weight: 500;
    }

    .file-actions {
        align-items: flex-start;
    }

    .action-buttons {
        display: flex;
        gap: 10px;
    }

    .action-btn {
        background: rgba(0, 255, 65, 0.1);
        border: 1px solid #00ff41;
        color: #00ff41;
        padding: 6px 12px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .action-btn:hover {
        background: rgba(0, 255, 65, 0.2);
        transform: translateY(-1px);
    }

    .download-btn:hover {
        box-shadow: 0 3px 10px rgba(0, 255, 65, 0.3);
    }

    /* Credential Field Actions */
    .credential-field {
        display: grid;
        grid-template-columns: 120px 1fr;
        gap: 15px;
        align-items: center;
    }

    .field-value-with-actions {
        display: flex;
        align-items: center;
        gap: 10px;
        justify-content: space-between;
    }

    .password-actions {
        display: flex;
        gap: 5px;
    }

    .copy-btn, .toggle-btn {
        background: rgba(0, 170, 255, 0.1);
        border: 1px solid #00aaff;
        color: #00aaff;
        padding: 4px 8px;
        border-radius: 3px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 30px;
        height: 28px;
    }

    .copy-btn:hover, .toggle-btn:hover {
        background: rgba(0, 170, 255, 0.2);
        transform: scale(1.05);
        box-shadow: 0 2px 8px rgba(0, 170, 255, 0.3);
    }

    .toggle-btn {
        background: rgba(255, 193, 7, 0.1);
        border-color: #ffc107;
        color: #ffc107;
    }

    .toggle-btn:hover {
        background: rgba(255, 193, 7, 0.2);
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
    }

    .copy-btn:active, .toggle-btn:active {
        transform: scale(0.95);
    }

    /* Responsive adjustments for credential fields */
    @media (max-width: 768px) {
        .credential-field {
            grid-template-columns: 1fr;
            gap: 5px;
        }

        .field-value-with-actions {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }

        .password-actions {
            align-self: flex-end;
        }
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

    .secret-actions {
        display: flex;
        gap: 5px;
        align-items: center;
    }

    .secret-action-btn {
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        padding: 8px;
        border-radius: 4px;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 32px;
        height: 32px;
    }

    .secret-action-btn:hover {
        background: rgba(255, 107, 107, 0.1);
        color: #ff6b6b;
        transform: scale(1.1);
    }

    .delete-btn {
        border: 1px solid transparent;
    }

    .delete-btn:hover {
        border-color: #ff6b6b;
        box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
    }

    .delete-icon {
        font-size: 1rem;
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

    /* Profile Content Styles */
    .profile-content {
        width: 100%;
    }

    .profile-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
    }

    .profile-status {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #00aaff;
        font-size: 0.9rem;
    }

    .profile-sections {
        display: grid;
        gap: 30px;
        max-width: 800px;
        margin: 0 auto;
    }

    /* Profile Modal Styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(5px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .modal-container {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        border: 2px solid #00ff41;
        border-radius: 10px;
        width: 90%;
        max-width: 600px;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 255, 65, 0.3);
        animation: slideIn 0.3s ease;
    }

    @keyframes slideIn {
        from { 
            transform: translateY(-50px);
            opacity: 0;
        }
        to { 
            transform: translateY(0);
            opacity: 1;
        }
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 25px;
        border-bottom: 1px solid #333;
        background: rgba(0, 0, 0, 0.6);
    }

    .modal-title {
        margin: 0;
        font-size: 1.2rem;
        color: #00ff41;
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
    }

    .modal-icon {
        font-size: 1.3rem;
    }

    .modal-close {
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid #ff6b6b;
        color: #ff6b6b;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1.2rem;
        font-weight: bold;
    }

    .modal-close:hover {
        background: rgba(255, 107, 107, 0.2);
        transform: scale(1.1);
        box-shadow: 0 0 15px rgba(255, 107, 107, 0.4);
    }

    .modal-body {
        padding: 25px;
        display: grid;
        gap: 30px;
    }

    /* MFA Setup Modal Styles */
    .mfa-modal {
        max-width: 900px;
        width: 95%;
    }

    .mfa-setup-content {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
        align-items: start;
    }

    .mfa-instructions {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid #333;
        border-radius: 8px;
        padding: 20px;
    }

    .instruction-title {
        color: #00aaff;
        font-size: 1rem;
        margin: 0 0 20px 0;
        font-weight: 500;
    }

    .instruction-steps {
        display: grid;
        gap: 20px;
        margin-bottom: 25px;
    }

    .step {
        display: flex;
        gap: 15px;
        align-items: flex-start;
    }

    .step-number {
        background: linear-gradient(45deg, #00aaff, #0088cc);
        color: #000;
        width: 25px;
        height: 25px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .step-content h4 {
        color: #00ff41;
        font-size: 0.9rem;
        margin: 0 0 8px 0;
        font-weight: 600;
    }

    .step-content p {
        color: #888;
        font-size: 0.8rem;
        margin: 0 0 8px 0;
        line-height: 1.4;
    }

    .step-content ul {
        margin: 0;
        padding-left: 15px;
        color: #888;
        font-size: 0.8rem;
    }

    .step-content li {
        margin-bottom: 3px;
    }

    .security-note {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 15px;
        display: flex;
        gap: 10px;
        align-items: flex-start;
    }

    .security-note .warning-icon {
        color: #ffc107;
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    .note-content {
        color: #ffc107;
        font-size: 0.8rem;
        line-height: 1.4;
    }

    .note-content strong {
        color: #ffc107;
        font-weight: 700;
    }

    .mfa-qr-section {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid #333;
        border-radius: 8px;
        padding: 20px;
        display: grid;
        gap: 20px;
    }

    .qr-title {
        color: #00aaff;
        font-size: 1rem;
        margin: 0;
        font-weight: 500;
        text-align: center;
    }

    .qr-code-wrapper {
        display: flex;
        justify-content: center;
        padding: 20px;
        background: #fff;
        border-radius: 8px;
        margin: 0 auto;
        width: fit-content;
    }

    .qr-code {
        width: 200px;
        height: 200px;
        border-radius: 5px;
    }

    .qr-loading {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 240px;
        background: rgba(0, 0, 0, 0.6);
        border: 2px dashed #333;
        border-radius: 8px;
        color: #888;
        font-size: 0.9rem;
    }

    .manual-entry {
        border-top: 1px solid #333;
        padding-top: 20px;
    }

    .manual-entry h4 {
        color: #00ff41;
        font-size: 0.9rem;
        margin: 0 0 15px 0;
        font-weight: 600;
    }

    .secret-key-container {
        display: grid;
        gap: 8px;
    }

    .secret-label {
        color: #888;
        font-size: 0.8rem;
        text-transform: lowercase;
    }

    .secret-value-container {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .secret-key {
        flex: 1;
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #333;
        color: #00ff41;
        padding: 10px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        word-break: break-all;
        overflow-wrap: break-word;
    }

    .verification-section {
        border-top: 1px solid #333;
        padding-top: 20px;
    }

    .verification-section h4 {
        color: #00ff41;
        font-size: 0.9rem;
        margin: 0 0 15px 0;
        font-weight: 600;
    }

    .verification-form {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .verification-input {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #333;
        color: #00ff41;
        padding: 12px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        text-align: center;
        letter-spacing: 3px;
        width: 120px;
    }

    .verification-input:focus {
        outline: none;
        border-color: #00aaff;
        box-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
    }

    .verify-btn {
        background: linear-gradient(45deg, #00ff41, #00cc33);
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
    }

    .verify-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 255, 65, 0.4);
    }

    .profile-section {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid #333;
        border-radius: 8px;
        padding: 20px;
    }

    .section-header {
        color: #00aaff;
        font-size: 1rem;
        margin: 0 0 20px 0;
        font-weight: 500;
        text-transform: lowercase;
    }

    .info-grid {
        display: grid;
        gap: 12px;
    }

    .info-item {
        display: grid;
        grid-template-columns: 150px 1fr;
        gap: 15px;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(51, 51, 51, 0.5);
    }

    .info-item:last-child {
        border-bottom: none;
    }

    .info-label {
        color: #888;
        font-size: 0.9rem;
        text-transform: lowercase;
    }

    .info-value {
        color: #00ff41;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .form-group {
        margin-bottom: 20px;
    }

    .form-label {
        display: block;
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 8px;
        text-transform: lowercase;
    }

    .profile-input {
        width: 100%;
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #333;
        color: #00ff41;
        padding: 12px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        box-sizing: border-box;
        transition: all 0.3s ease;
    }

    .profile-input:focus {
        outline: none;
        border-color: #00aaff;
        box-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
    }

    .profile-input:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        color: #666;
    }

    .profile-action-btn {
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
        width: 100%;
        justify-content: center;
    }

    .profile-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 170, 255, 0.4);
    }

    .profile-action-btn.primary {
        background: linear-gradient(45deg, #00ff41, #00cc33);
    }

    .profile-action-btn.primary:hover {
        box-shadow: 0 5px 15px rgba(0, 255, 65, 0.4);
    }

    .profile-action-btn.secondary {
        background: linear-gradient(45deg, #ffc107, #ff9800);
        color: #000;
    }

    .profile-action-btn.secondary:hover {
        box-shadow: 0 5px 15px rgba(255, 193, 7, 0.4);
    }

    .profile-action-btn.danger {
        background: linear-gradient(45deg, #ff6b6b, #ff5252);
        color: #fff;
    }

    .profile-action-btn.danger:hover {
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
    }
.profile-action-btn:disabled {
    background: rgba(102, 102, 102, 0.3) !important;
    color: #666 !important;
    cursor: not-allowed;
    transform: none !important;
    box-shadow: none !important;
    opacity: 0.6;
}

    .security-warning {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #ffc107;
        font-size: 0.85rem;
    }

    .warning-icon {
        font-size: 1.2rem;
    }

    .security-info {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 20px;
        align-items: center;
        padding: 15px;
        background: rgba(0, 170, 255, 0.05);
        border: 1px solid rgba(0, 170, 255, 0.2);
        border-radius: 5px;
    }

    .security-description {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .security-icon {
        font-size: 1.5rem;
        color: #00aaff;
    }

    .security-text h4 {
        margin: 0 0 5px 0;
        color: #00aaff;
        font-size: 0.95rem;
        font-weight: 600;
    }

    .security-text p {
        margin: 0;
        color: #888;
        font-size: 0.8rem;
        line-height: 1.4;
    }

    .security-info .profile-action-btn {
        width: auto;
        min-width: 140px;
    }

    .danger-zone {
        display: grid;
        gap: 20px;
    }

    .danger-item {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 20px;
        align-items: center;
        padding: 15px;
        background: rgba(255, 107, 107, 0.05);
        border: 1px solid rgba(255, 107, 107, 0.2);
        border-radius: 5px;
    }

    .danger-info h4 {
        margin: 0 0 5px 0;
        color: #ff6b6b;
        font-size: 0.95rem;
        font-weight: 600;
    }

    .danger-info p {
        margin: 0;
        color: #888;
        font-size: 0.8rem;
        line-height: 1.4;
    }

    .danger-item .profile-action-btn {
        width: auto;
        min-width: 140px;
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

        /* Modal Responsive */
        .modal-container {
            width: 95%;
            margin: 10px;
        }

        .modal-header {
            padding: 15px 20px;
        }

        .modal-title {
            font-size: 1rem;
        }

        .modal-body {
            padding: 20px;
        }

        .info-item {
            grid-template-columns: 1fr;
            gap: 5px;
        }

        .danger-item {
            grid-template-columns: 1fr;
            gap: 15px;
            text-align: center;
        }

        .danger-item .profile-action-btn {
            width: 100%;
        }

        /* Profile Content Responsive */
        .profile-sections {
            max-width: none;
        }

        .profile-header {
            flex-direction: column;
            gap: 15px;
            text-align: center;
        }

        /* MFA Modal Responsive */
        .mfa-modal {
            width: 98%;
            max-height: 95vh;
            overflow-y: auto;
        }

        .mfa-setup-content {
            grid-template-columns: 1fr;
            gap: 20px;
        }

        .qr-code {
            width: 150px;
            height: 150px;
        }

        .verification-form {
            flex-direction: column;
            gap: 15px;
            align-items: stretch;
        }

        .verification-input {
            width: 100%;
            text-align: center;
        }

        .verify-btn {
            width: 100%;
            justify-content: center;
        }
    }
/* Add this to your existing styles */

/* Confirmation Modal Styles */
.confirm-modal {
    max-width: 500px;
    width: 90%;
}

.warning-content {
    display: grid;
    gap: 25px;
}

.warning-message {
    display: flex;
    gap: 15px;
    align-items: flex-start;
}

.warning-message .warning-icon {
    color: #ff6b6b;
    font-size: 2rem;
    flex-shrink: 0;
}

.warning-text h3 {
    color: #ff6b6b;
    font-size: 1.1rem;
    margin: 0 0 15px 0;
    font-weight: 700;
}

.warning-text p {
    color: #888;
    font-size: 0.9rem;
    margin: 0 0 15px 0;
    line-height: 1.4;
}

.warning-text ul {
    color: #888;
    font-size: 0.9rem;
    margin: 0 0 15px 0;
    padding-left: 20px;
}

.warning-text li {
    margin-bottom: 5px;
}

.warning-text strong {
    color: #ff6b6b;
    font-weight: 700;
}

.confirm-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}

.confirm-btn {
    padding: 12px 20px;
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: none;
    text-transform: uppercase;
}

.confirm-btn.cancel {
    background: rgba(102, 102, 102, 0.3);
    color: #888;
    border: 1px solid #666;
}

.confirm-btn.cancel:hover {
    background: rgba(102, 102, 102, 0.5);
    color: #aaa;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 102, 102, 0.3);
}

.confirm-btn.delete {
    background: linear-gradient(45deg, #ff6b6b, #ff5252);
    color: #fff;
    border: 1px solid #ff6b6b;
}

.confirm-btn.delete:hover {
    background: linear-gradient(45deg, #ff5252, #ff4444);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(255, 107, 107, 0.5);
}

.confirm-btn:active {
    transform: translateY(0);
}

/* Mobile responsive */
@media (max-width: 768px) {
    .confirm-actions {
        grid-template-columns: 1fr;
        gap: 10px;
    }
    
    .warning-message {
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }
}
    /* Add Secret Sidebar Styles */
    .add-secret-sidebar {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #333;
    }

    .sidebar-header {
        margin-bottom: 15px;
    }

    .sidebar-title {
        font-size: 0.9rem;
        color: #888;
        margin: 0;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .sidebar-dropdown-section {
        margin-bottom: 20px;
    }

    .dropdown-label {
        display: block;
        font-size: 0.8rem;
        color: #888;
        margin-bottom: 8px;
        font-family: 'JetBrains Mono', monospace;
        text-transform: lowercase;
    }

    .sidebar-dropdown {
        width: 100%;
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #333;
        color: #00ff41;
        padding: 10px 12px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        appearance: none;
        background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='%2300ff41' viewBox='0 0 16 16'%3e%3cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3e%3c/svg%3e");
        background-repeat: no-repeat;
        background-position: right 12px center;
        background-size: 12px;
        padding-right: 35px;
    }

    .sidebar-dropdown:hover {
        border-color: #00ff41;
        background-color: rgba(0, 255, 65, 0.05);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 255, 65, 0.2);
    }

    .sidebar-dropdown:focus {
        outline: none;
        border-color: #00aaff;
        box-shadow: 0 0 0 2px rgba(0, 170, 255, 0.3);
    }

    .sidebar-form {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
/* Add these styles to your existing <style> section */

/* Edit button styling */
.edit-btn {
    background: rgba(0, 170, 255, 0.1);
    border: 1px solid #00aaff;
    color: #00aaff;
}

.edit-btn:hover {
    background: rgba(0, 170, 255, 0.2);
    border-color: #00aaff;
    box-shadow: 0 2px 8px rgba(0, 170, 255, 0.3);
}

.update-btn {
    background: rgba(0, 170, 255, 0.1);
    border: 1px solid #00aaff;
    color: #00aaff;
}

.update-btn:hover {
    background: rgba(0, 170, 255, 0.2);
    border-color: #00aaff;
    box-shadow: 0 2px 8px rgba(0, 170, 255, 0.3);
}

.edit-icon, .update-icon {
    font-size: 1rem;
}

/* Edit Modal Styles */
.edit-modal {
    max-width: 600px;
    width: 95%;
}

.edit-content {
    width: 100%;
}

.edit-form {
    display: grid;
    gap: 25px;
}

.form-section {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid #333;
    border-radius: 8px;
    padding: 20px;
}

.form-section-title {
    color: #00aaff;
    font-size: 1rem;
    margin: 0 0 20px 0;
    font-weight: 500;
    text-transform: lowercase;
}

.edit-input, .edit-textarea {
    width: 100%;
    background: rgba(0, 0, 0, 0.6);
    border: 1px solid #333;
    color: #00ff41;
    padding: 12px;
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    box-sizing: border-box;
    transition: all 0.3s ease;
}

.edit-input:focus, .edit-textarea:focus {
    outline: none;
    border-color: #00aaff;
    box-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
}

.edit-textarea {
    resize: vertical;
    min-height: 80px;
}

.edit-input::placeholder, .edit-textarea::placeholder {
    color: #666;
    font-style: italic;
}

/* Current file info styling */
.current-file-info {
    background: rgba(0, 170, 255, 0.05);
    border: 1px solid rgba(0, 170, 255, 0.2);
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
}

.file-info-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 15px;
}

.file-icon {
    font-size: 1.2rem;
}

.current-file-label {
    color: #00aaff;
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
}

.file-details {
    display: grid;
    gap: 8px;
    margin-bottom: 15px;
}

.file-detail {
    display: grid;
    grid-template-columns: 80px 1fr;
    gap: 10px;
    align-items: center;
}

.detail-label {
    color: #888;
    font-size: 0.8rem;
    text-transform: lowercase;
}

.detail-value {
    color: #00ff41;
    font-size: 0.8rem;
    font-weight: 500;
}

.file-actions {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.file-action-btn {
    background: rgba(0, 255, 65, 0.1);
    border: 1px solid #00ff41;
    color: #00ff41;
    padding: 8px 12px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 5px;
}

.file-action-btn:hover {
    background: rgba(0, 255, 65, 0.2);
    transform: translateY(-1px);
    box-shadow: 0 3px 10px rgba(0, 255, 65, 0.3);
}

.file-note {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 10px;
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid rgba(255, 193, 7, 0.3);
    border-radius: 5px;
}

.note-icon {
    color: #ffc107;
    font-size: 1rem;
    flex-shrink: 0;
}

.note-text {
    color: #ffc107;
    font-size: 0.8rem;
    line-height: 1.4;
}

/* Edit actions */
.edit-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin-top: 20px;
}

.edit-btn {
    padding: 12px 20px;
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: none;
    text-transform: uppercase;
}

.edit-btn.cancel {
    background: rgba(102, 102, 102, 0.3);
    color: #888;
    border: 1px solid #666;
}

.edit-btn.cancel:hover {
    background: rgba(102, 102, 102, 0.5);
    color: #aaa;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 102, 102, 0.3);
}

.edit-btn.save {
    background: linear-gradient(45deg, #00aaff, #0088cc);
    color: #000;
    border: 1px solid #00aaff;
}

.edit-btn.save:hover:not(:disabled) {
    background: linear-gradient(45deg, #0088cc, #0066aa);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 170, 255, 0.5);
}

.edit-btn.save:disabled {
    background: rgba(102, 102, 102, 0.3);
    color: #666;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
    opacity: 0.6;
}

.edit-btn:active:not(:disabled) {
    transform: translateY(0);
}

/* Mobile responsive */
@media (max-width: 768px) {
    .edit-actions {
        grid-template-columns: 1fr;
        gap: 10px;
    }
    
    .file-detail {
        grid-template-columns: 1fr;
        gap: 5px;
    }
    
    .file-actions {
        flex-direction: column;
    }
    
    .file-action-btn {
        width: 100%;
        justify-content: center;
    }
}
    .sidebar-input {
        width: 100%;
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #333;
        color: #00ff41;
        padding: 10px 12px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-sizing: border-box;
    }

    .sidebar-input:hover {
        border-color: #00ff41;
        background-color: rgba(0, 255, 65, 0.05);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 255, 65, 0.2);
    }

    .sidebar-input:focus {
        outline: none;
        border-color: #00aaff;
        background-color: rgba(0, 170, 255, 0.08);
        box-shadow: 0 0 0 2px rgba(0, 170, 255, 0.3);
        transform: translateY(-1px);
    }

    .sidebar-input::placeholder {
        color: #666;
        font-style: italic;
    }

    .sidebar-textarea {
        width: 100%;
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #333;
        color: #00ff41;
        padding: 10px 12px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        resize: vertical;
        min-height: 60px;
        box-sizing: border-box;
    }

    .sidebar-textarea:hover {
        border-color: #00ff41;
        background-color: rgba(0, 255, 65, 0.05);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 255, 65, 0.2);
    }

    .sidebar-textarea:focus {
        outline: none;
        border-color: #00aaff;
        background-color: rgba(0, 170, 255, 0.08);
        box-shadow: 0 0 0 2px rgba(0, 170, 255, 0.3);
        transform: translateY(-1px);
    }

    .sidebar-textarea::placeholder {
        color: #666;
        font-style: italic;
    }

    .sidebar-add-btn {
        background: linear-gradient(45deg, #00ff41, #00cc33);
        border: none;
        color: #000;
        padding: 12px 16px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-top: 8px;
        text-transform: uppercase;
    }

    .sidebar-add-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 255, 65, 0.4);
        background: linear-gradient(45deg, #00ff41, #00aa2a);
    }

    .sidebar-add-btn:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(0, 255, 65, 0.3);
    }

    .sidebar-add-btn.disabled,
    .sidebar-add-btn:disabled {
        background: rgba(102, 102, 102, 0.3);
        color: #666;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }

    .sidebar-add-btn.disabled:hover,
    .sidebar-add-btn:disabled:hover {
        background: rgba(102, 102, 102, 0.3);
        transform: none;
        box-shadow: none;
    }

    .vault-required-notice {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 8px;
        padding: 6px 10px;
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 4px;
        font-size: 0.8rem;
    }

    .warning-icon {
        color: #ffc107;
        font-size: 0.9rem;
    }

    .notice-text {
        color: #ffc107;
        font-style: italic;
    }

    .sidebar-file-upload {
        display: block;
        background: rgba(0, 0, 0, 0.8);
        border: 2px dashed #333;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'JetBrains Mono', monospace;
    }

    .sidebar-file-upload:hover {
        border-color: #00aaff;
        background: rgba(0, 170, 255, 0.05);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 170, 255, 0.2);
    }

    .file-upload-text {
        color: #00aaff;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .sidebar-file-info {
        background: rgba(0, 170, 255, 0.1);
        border: 1px solid #00aaff;
        border-radius: 5px;
        padding: 8px 12px;
        font-size: 0.8rem;
        color: #00aaff;
        margin-top: 8px;
    }

    .file-detail {
        display: block;
        margin-bottom: 4px;
    }

    .file-detail:last-child {
        margin-bottom: 0;
    }
    /* Add this to your existing styles */

.password-confirmation {
    background: rgba(255, 107, 107, 0.05);
    border: 1px solid rgba(255, 107, 107, 0.2);
    border-radius: 8px;
    padding: 20px;
    margin: 10px 0;
}

.password-confirm-input {
    background: rgba(0, 0, 0, 0.8) !important;
    border: 2px solid #ff6b6b !important;
    color: #ff6b6b !important;
}

.password-confirm-input:focus {
    border-color: #ff5252 !important;
    box-shadow: 0 0 15px rgba(255, 107, 107, 0.4) !important;
}

.password-confirm-input::placeholder {
    color: rgba(255, 107, 107, 0.6);
    font-style: italic;
}

.confirm-btn.delete.disabled,
.confirm-btn.delete:disabled {
    background: rgba(102, 102, 102, 0.3) !important;
    color: #666 !important;
    cursor: not-allowed;
    transform: none !important;
    box-shadow: none !important;
    opacity: 0.6;
}

/* Password Input Section Styles */
.password-input-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.password-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
}

.generate-password-btn,
.toggle-password-btn,
.copy-password-btn {
    padding: 6px 8px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 3px;
    text-transform: uppercase;
    min-height: 32px;
    white-space: nowrap;
    overflow: hidden;
}

.generate-password-btn {
    background: rgba(0, 170, 255, 0.1);
    border: 1px solid #00aaff;
    color: #00aaff;
}

.generate-password-btn:hover:not(:disabled) {
    background: rgba(0, 170, 255, 0.2);
    transform: translateY(-1px);
    box-shadow: 0 3px 10px rgba(0, 170, 255, 0.3);
}

.generate-password-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.toggle-password-btn {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid #ffc107;
    color: #ffc107;
}

.toggle-password-btn:hover {
    background: rgba(255, 193, 7, 0.2);
    transform: translateY(-1px);
    box-shadow: 0 3px 10px rgba(255, 193, 7, 0.3);
}

.copy-password-btn {
    background: rgba(0, 255, 65, 0.1);
    border: 1px solid #00ff41;
    color: #00ff41;
}

.copy-password-btn:hover:not(:disabled) {
    background: rgba(0, 255, 65, 0.2);
    transform: translateY(-1px);
    box-shadow: 0 3px 10px rgba(0, 255, 65, 0.3);
}

.copy-password-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
}

.generate-icon,
.toggle-icon,
.copy-icon {
    font-size: 0.9rem;
    transition: transform 0.3s ease;
    flex-shrink: 0;
}

.button-text {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    white-space: nowrap;
}

.generate-password-btn:hover:not(:disabled) .generate-icon {
    transform: rotate(180deg);
}

/* Mobile responsive */
@media (max-width: 768px) {
    .password-buttons {
        grid-template-columns: 1fr;
        gap: 8px;
    }
    
    .generate-password-btn,
    .toggle-password-btn,
    .copy-password-btn {
        width: 100%;
        justify-content: center;
        padding: 10px 16px;
    }
    
    .button-text {
        font-size: 0.8rem;
    }
}
</style>