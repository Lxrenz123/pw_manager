
<script>
  import { Router, Link, Route, navigate } from "svelte-routing";
  import Register from './pages/Register.svelte';
  import Login from './pages/Login.svelte'; 
  import App from './pages/App.svelte';
  import MFA from './pages/MFA.svelte';
  import { documentSchema, noteSchema, credentialSchema} from './script/schema.js'

</script>



<Router>
  <Route path="/login">
    <Login />
  </Route>
  <Route path="/register">
    <Register />
  </Route>
  <Route path="/app">
  <App />
  </Route>
  <Route path="/mfa">
  <MFA />
  </Route>
</Router>

