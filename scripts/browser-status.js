const h = require('/Users/Treydong/.openclaw/skills/browser-automation/index.js');
h.handleStatus().then(r => console.log(JSON.stringify(r, null, 2))).catch(e => console.error(e.message));
