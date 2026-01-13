# Simbuster_translations

Minimal translation project skeleton.

## Files

- `translations.json` — example translation data for multiple locales.

## Usage (examples)

Node.js:

```js
const fs = require('fs');
const translations = JSON.parse(fs.readFileSync('translations.json', 'utf8'));
console.log(translations.translations.en.greeting);
```

Python:

```py
import json
with open('translations.json') as f:
    data = json.load(f)
print(data['translations']['en']['greeting'])
```

## Next steps

- Add more locales and keys under `translations`.
- Add a JSON Schema or validator script if you want to enforce structure.
- Ask me to initialize git or add a license.
