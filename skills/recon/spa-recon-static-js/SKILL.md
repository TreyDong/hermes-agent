---
name: spa-recon-static-js
description: Extract navigation, services, and API structure from Vue/React SPA static JS bundles when curl/web tools return empty HTML
---

# SPA Recon: Extract Content from Static JS Bundles

## When to Use

Target website is a modern SPA (Vue/React/Angular with hash routing) and:
- `curl` on the main URL returns minimal/empty HTML (just `<div id="app">`)
- `web_extract` or direct HTTP requests return nothing useful
- Common routes (`/about`, `/products`, `/contact`) return 404
- You need to understand the site's structure, navigation, features, or business logic

## Technique

For SPA sites using hash routing (`/#/`, `/#/index/about`), the **static JS bundle** at `/static/js/app.*.js` contains the entire frontend application including:
- Navigation menu labels and routes
- Feature flags and product/service names
- API endpoint paths
- i18n string tables
- Business logic and configuration

## Step-by-Step

### Step 1: Probe the main domain
```bash
curl -s --max-time 15 "https://TARGET.com" -H "Accept: text/html" -L
```
Check the `<title>` tag and look for `<div id="app">` (confirms SPA).

### Step 2: Find the JS bundle URL
```bash
# Extract all script src references
curl -s --max-time 15 "https://TARGET.com" -H "Accept: text/html" -L \
  | grep -oE 'src="[^"]*\.js"' | sort -u
```
Look for patterns like `/static/js/app.[hash].js` or `/js/app.[hash].js`.

### Step 3: Fetch the main JS bundle
```bash
# Use the discovered URL (often has a hash in filename, try without hash first)
curl -s --max-time 30 "https://TARGET.com/static/js/app.ac25ae6b.js" \
  | grep -oE '"[A-Za-z ]{3,}":"[^"]{3,100}"' | head -100

# Also grep for route/feature keywords
curl -s --max-time 30 "https://TARGET.com/static/js/app.ac25ae6b.js" \
  | grep -oE '(products|services|about|contact|api|endpoint)' | sort -u
```

### Step 4: Extract i18n/translation tables (high value)
```bash
# Often contain full menu labels and UI strings
curl -s --max-time 30 "https://TARGET.com/static/js/app.*.js" \
  | grep -oE '"[A-Za-z]{2,}":"[^"]{3,50}"' | sort -u | head -100
```

### Step 5: Extract API paths
```bash
curl -s --max-time 30 "https://TARGET.com/static/js/app.*.js" \
  | grep -oE '"/[a-z/_-]{5,50}"' | sort -u | head -50
```

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| JS filename has hash (e.g. `app.ac25ae6b.js`) | Try without hash: `/static/js/app.js` or find via HTML source |
| Output too large | Pipe to `grep` with keyword filters rather than reading full file |
| Empty result from main JS | Try `vendors~app.*.js` (dependency bundle, often contains i18n) |
| Site uses Odoo CMS | Odoo 11 static bundles often have navigation in `/web/content/` paths |

## Real Example

GreenGrid (`greengrid.cn`) - Vue SPA, curl returned minimal HTML:
```bash
# Found navigation structure and full service list in the JS bundle
curl -s --max-time 15 "https://www.greengridvcm.com/static/js/app.ac25ae6b.js" \
  | grep -oE '"[A-Za-z]{2,}":"[^"]{3,50}"' | head -100
# Output: Logistics Service, R&D Institute, Inspection Service, Customized Service, etc.
```

## Verification

After extracting, cross-reference findings:
- Try `/#/route-name` paths in browser if available
- Check `/new-website/index.html` for hash-routed SPAs
- Look for `window.__INITIAL_STATE__` or similar data hydration patterns in the HTML

## Critical Lessons Learned

### Lesson 1: Always verify download success with byte count
`curl` can return exit code 0 but write 0 bytes when the site redirects or the JS URL has a content hash. **Always** run:
```bash
curl -sL "https://TARGET.com/static/js/app.js" -o app.js && wc -c app.js
# Must show >0 bytes before proceeding
```
If 0 bytes: try different URL patterns (add/remove `/static/`, try `vendors~app.*.js` instead).

### Lesson 2: Use Python, not shell grep, for minified JS with Chinese/obfuscated text
Shell `grep` and `rg` fail on Chinese characters in minified bundles (range errors, encoding issues). Use `execute_code` with Python:
```python
import re
with open('app.js', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Extract Chinese text
chinese = re.findall(r'[\u4e00-\u9fff]{2,50}', content)
# Deduplicate while preserving order
seen = set(); result = []
for c in chinese:
    if c not in seen:
        seen.add(c); result.append(c)
for c in result: print(c)
```

### Lesson 3: meta description is a product catalog goldmine
The `<meta name="description">` tag in Vue SPA HTML headers often contains a full enumerated product list in English, including all category names and product types. Always extract it:
```python
meta = re.search(r'<meta name="description" content="([^"]+)"', html_content)
if meta:
    print(meta.group(1))
```

### Lesson 4: webpackJsonp bundle format
Vue/React apps use webpack, which wraps code in `window["webpackJsonp"]=window["webpackJsonp"]||[]).push(...)`. The JS content starts after the webpack bootstrap and is the actual app code. Don't be alarmed by the unusual format—this is normal and the text is still extractable via Python regex.

### Lesson 5: wget mirror fails silently on SPAs
`wget --mirror` often produces 0 files for Vue SPAs because the crawler doesn't execute JS to discover routes. Do not rely on it. Always fall back to: (1) curl the HTML to find JS bundle URLs, (2) curl the JS bundle, (3) parse with Python.
