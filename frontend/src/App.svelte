<script>
  import { Router, Link, Route, navigate } from "svelte-routing";
  import Register from './pages/Register.svelte';
  import Login from './pages/Login.svelte'; 
  import App from './pages/App.svelte';

</script>

<Router>

  <Route path="/">
    <Login />
  </Route>
  
  <Route path="/login">
    <Login />
  </Route>
  <Route path="/register">
    <Register />
  </Route>
  <Route path="/app">
  <App />
  </Route>
</Router>
