# POST.json — exact format (fill in after the X post exists)

The X post does not exist yet, so this repository deliberately has NO
POST.json yet. The moment the meme is posted from a public X account,
create `POST.json` at the repository root with exactly this shape
(from the kit's RULES.txt, "The post file"):

```json
{"url": "https://x.com/<handle>/status/<id>"}
```

Rules for the value:

- `url` is the post's address as X shows it: `https://x.com/<handle>/status/<id>`
  (the same on twitter.com, with optional `www.` or `mobile.`, or the
  `/i/web/status/<id>` form, are also read).
- `<id>` is digits only; a query string or fragment after it is read past.
- POST.json must be a JSON object of at most 16384 bytes.
- `main.ts` copies POST.json to `/output/POST.json`; that is all it does.
  Nothing the program writes about the post is judged — the house reads
  the post itself from X.

Gate reminders for the post itself (a post missing any of these is refused
and cannot be edited — it must be posted again):

- Posted at or after the opening (2026-11-19T14:00:00Z) and before the
  deadline (2026-11-23T14:00:00Z), from a public (not protected) account.
- Its text carries make.fun (the bounty link counts) and/or a tag of
  `@makefunai`, AND one of the account's play codes for this bounty.
- Its first picture is the meme (PNG, JPEG or WebP — not a GIF or video).
- No earlier entry of another account names the same post.
