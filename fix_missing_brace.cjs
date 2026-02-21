const fs = require('fs');
const path = require('path');

const clientPath = path.join(__dirname, 'src/features/landing/components/LandingClient.tsx');
let content = fs.readFileSync(clientPath, 'utf8');

// Remove the stray return () => ctx.revert()
content = content.replace(/return \(\) => ctx\.revert\(\);\n\s*\}, \[isLoaded\]\);/, '');

// Remove the duplicated Demo autoplay hook entirely (since we added it at the top)
content = content.replace(/\/\/ Demo autoplay\n\s*useEffect\(\(\) => \{\n\s*if \(\!isPlaying\) return;\n\s*const interval = setInterval\(\(\) => \{\n\s*setActiveDemo\(\(prev\) => \(prev \+ 1\) % 4\);\n\s*\}, 4000\);\n\s*return \(\) => clearInterval\(interval\);\n\s*\}, \[isPlaying\]\);/, '');

fs.writeFileSync(clientPath, content);
console.log("Fixed LandingClient.tsx syntax");
