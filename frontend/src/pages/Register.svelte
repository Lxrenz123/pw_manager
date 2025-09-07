<script>
    import { apiBase } from "../script/api-base-url";


    let email = "";
    let password = "";
    let result;

async function register(){

    const response = await fetch(`${apiBase}/user/`, {
        method: "POST",
        headers: {
        'Content-Type': "application/json",
        'accept': "application/json"
        },
        body: JSON.stringify({email, password})
    });

    const data = await response.json();

    if (!response.ok){
        result = data.detail;
        throw new Error("Failed");
    }

    return "Successful registered!";

}
</script>



<form class="register-form" on:submit|preventDefault={register}>
  {result}
<label for="username">Username</label>
<input id="username" name="username" type="text" placeholder="Your Username.." bind:value={email}/><br>
 <label for="password" >Password</label>
 <input type="text" name="password" id="password" placeholder="Your Password.." bind:value={password}/><br>
 <input type="submit" value="Submit"/><br>

</form>

<a href="/login"> Log in</a>
