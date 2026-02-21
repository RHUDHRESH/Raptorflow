const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, 'src/features/landing/components/LandingClient.tsx');
let lines = fs.readFileSync(file, 'utf8').split('\n');
// Ensure we are deleting the right lines by checking content
let startIndex = -1;
let endIndex = -1;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('return () => ctx.revert();')) {
        startIndex = i;
    }
    if (startIndex !== -1 && i > startIndex && lines[i].includes('}, [isPlaying]);')) {
        endIndex = i;
        break;
    }
}

if (startIndex !== -1 && endIndex !== -1) {
    lines.splice(startIndex, (endIndex - startIndex) + 1);
    fs.writeFileSync(file, lines.join('\n'));
    console.log("Successfully sliced out stray text block");
} else {
    console.log("Could not find blocks to slice");
}
