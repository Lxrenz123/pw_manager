<script>
    import { onMount } from "svelte";
    import { apiBase } from "../script/api-base-url";
    
    let vaults = $state([]);
    let noVaults;
    let vaultName = $state("");

    onMount(async () => {
        getVaults();
    });

async function getVaults(){
    const response = await fetch(`${apiBase}vault/`, {
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
       const response = await fetch(`${apiBase}vault/`, {
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

</script>

{#each vaults as vault}
    <div class="vault-item">
        <h3>{vault.name}</h3>
    </div>
{/each}




<input class="input-vault-name" bind:value={vaultName} />
<button class="add-vault-btn" on:click={addVault}>Vault hinzufügen</button>

<style>
#add-vault{
background-color: blue;
}
#add-vault:hover{
    font-size: 30px;
    cursor: pointer;

}

</style>