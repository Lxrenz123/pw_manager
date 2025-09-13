export const noteSchema = {
    type: "note",
    fields: {   
        content: { type: "string", required: true }
    }
}

export const credentialSchema = {
    type: "credential",
    fields: {
        username: { type: "string", required: false },
        password: { type: "string", required: false},
        url: { type: "string", required: false},
        note: { type: "string", required: false}, 
    }
}

export const documentSchema = {
    type: "document",
    fields: {
        filename: { required: true },
        blob: { required: true } 
    }
}