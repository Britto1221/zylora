# Chatbot and documents

Documents can be entered as text, extracted from supported uploaded assets, then
chunked and indexed per tenant. Retrieval is isolated by `tenant_id`.

The local implementation uses deterministic embeddings and lexical/vector
retrieval so development works without an external model. When an OpenAI key is
configured, the AI gateway can generate a grounded response from retrieved
context.

Every response includes source citations. When evidence is insufficient, the
chatbot returns the configured contact-form fallback instead of inventing facts.
