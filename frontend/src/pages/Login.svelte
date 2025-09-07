<script>
    import { navigate } from "svelte-routing";
    import { apiBase } from "../script/api-base-url";

    let email = "";
    let password = "";
    let result = "";


    async function login(){
    const response = await fetch( `${apiBase}auth/login`, {
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
    navigate("/app");
    return "Successfully logged in!";

}


</script>

<main>
 
  <div class="result" >{result} </div><br>
<form class="login-form" on:submit|preventDefault={login}>
  
<label for="username">Username</label>
<input id="username" name="username" type="text" placeholder="Your Username.." bind:value={email}/><br>
 <label for="password" >Password</label>
 <input type="text" name="password" id="password" placeholder="Your Password.." bind:value={password}/><br>
 <input type="submit" value="Submit"/><br>

</form>
<a href="/register"> Register now!</a>

</main>


<style>

.result{
    color: red;
}



</style>


