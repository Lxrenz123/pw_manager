
import { navigate } from "svelte-routing";
import { userKey } from "../stores/user-key.js";

export async function deriveKey(password, salt){

   const enc = new TextEncoder();
   const pwBytes = enc.encode(password);

   const pwKey = await crypto.subtle.importKey(
      "raw",
      pwBytes,
      "PBKDF2",
      false,
      ["deriveKey"]
   )



   const key = await crypto.subtle.deriveKey(
      {
         name: "PBKDF2",
         salt,
         iterations: 750_000,
         hash: "SHA-256"
      },
      pwKey,
      { name: "AES-GCM", length: 256},
      true,
      ["encrypt", "decrypt"]
   );



   return {
      key
   };



}

export async function loginCrypto(data, password){

   

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
    localStorage.removeItem("preauth_token");
    return "Successfully logged in!";

}




