



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




