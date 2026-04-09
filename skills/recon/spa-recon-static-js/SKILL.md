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
