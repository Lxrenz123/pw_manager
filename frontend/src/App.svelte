<script>
    let email = "";
    let password = "";

async function Login(){
    const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'accept': "application/json"
        },
        body: JSON.stringify({ email, password })
    });
    if (!response.ok){
        throw new Error("Failed")
    }
    console.log(response);
    return response.json();
}

</script>

<main>
  
</main>


<form class="login-form" on:submit|preventDefault={Login}>
<label for="username">Username</label>
<p><input id="username" name="username" type="text" placeholder="Your Username.." bind:value={email}/></p> 
 <label for="password" >Password</label>
 <input type="text" name="password" id="password" placeholder="Your Password.." bind:value={password}/>
 <input type="submit" value="Submit"/>
</form>

<style>

.login-form{
    padding: 50px;
    background-color: green;
}
</style>
