## 2024-06-25 — External Dependencies & Background Tasks Self-Healing
**Failure point found:** 1. External API calls (Algolia, SendGrid, Cloudinary) failed silently on transient network issues. 2. Critical background alert tasks (\`asyncio.create_task\`) could be silently destroyed mid-execution by the garbage collector due to lack of strong references.
**Why it existed:** 1. Rapid prototyping didn't account for transient failure. 2. Common misunderstanding of asyncio task lifecycle.
**Recovery built:** 1. Added \`with_retry\` mechanism with exponential backoff and \`inspect.isawaitable\` to handle \`asyncio.to_thread\` wrapping. 2. Added a strong reference \`set\` for background tasks, removed via \`.add_done_callback\`.
**Blast radius before:** 1. Occasional lost districts/emails/reports, confusing users. 2. Silent failure of critical outbreak alerts.
**Watch for:** 1. Other external API wrappers not using \`with_retry\`. 2. Any other uses of \`asyncio.create_task\` missing strong references.
