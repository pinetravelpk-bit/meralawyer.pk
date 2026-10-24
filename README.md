# MeraLawyer.pk website

A 30-page, fast, static website built for Google SEO, answer engines (AEO) and AI assistants (GEO).

## Folders
- `site/`: the finished website. Upload the CONTENTS of this folder to your hosting's `public_html`.
- `content.py`: all text, services, FAQs, phone, address. Edit here.
- `build.py`: regenerates `site/` after you edit content. Run `python3 build.py` (needs Python 3 and Pillow).
- `static/`: CSS, JavaScript and .htaccess copied into every build.

## Before going live (important)
1. In `content.py` → `CONFIG`, fill in: phone, WhatsApp number, email, both office addresses,
   reviewing advocate's name, and social profile URLs. Then run `python3 build.py`.
2. Search the site for `[` to find remaining placeholders: `[PRICE]`, `[Client name]`, `[YEAR]`,
   `[FOUNDER NAME…]`, About page text. Replace with real information (never invent reviews).
3. Have a lawyer review the legal content, the privacy policy and the disclaimer.

## After going live
1. Google Search Console: verify meralawyer.pk, submit `https://meralawyer.pk/sitemap.xml`.
2. Bing Webmaster Tools: import from Search Console (Bing powers ChatGPT search and Copilot).
3. Google Business Profile: create one for the Islamabad and one for the Rawalpindi office with
   EXACTLY the same name, address and phone as on the website. This drives "lawyer near me" results.
4. Get listed with the same details on Pakistani directories and social profiles, then add their URLs
   to `CONFIG` so they appear in the `sameAs` schema.
5. Ask real clients for Google reviews.
6. Test: https://search.google.com/test/rich-results and https://pagespeed.web.dev

## What is built in
- Unique title, meta description and canonical URL on every page; Open Graph and Twitter cards; geo tags
- JSON-LD schema: LegalService/Organization (both offices), WebSite, BreadcrumbList, Service, HowTo,
  FAQPage, ItemList, Speakable; reviewer and last-updated dates (E-E-A-T)
- Answer-first "Quick answer" box on every page, question-based headings, FAQs (AEO)
- `llms.txt` and `llms-full.txt` for AI assistants; `robots.txt` welcoming Google, Bing, ChatGPT,
  Claude, Perplexity, Gemini and Apple crawlers (GEO)
- `sitemap.xml`, 404 page, `.htaccess` (HTTPS, non-www, caching, compression)
- No framework: plain HTML/CSS, about 4 KB of JavaScript; works without JavaScript
- Mobile-friendly, keyboard accessible, respects reduced-motion settings
- The contact forms open WhatsApp with the visitor's details filled in, so no server is needed

## Growing traffic (next steps)
Add a `/guides/` section with articles answering real questions people search, e.g.
"khula procedure in Urdu", "how to verify property in Rawalpindi", "FBR tax return deadline 2026".
Fresh, specific, expert-reviewed content is what ranks and gets cited by AI tools.
