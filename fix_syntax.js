import fs from 'fs';

const filePath = 'c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\src\\pages\\app\\MuseChatPage.jsx';

let content = fs.readFileSync(filePath, 'utf8');

// Replace the problematic line
content = content.replace(/ {18}\)}\)/g, '                  ))');

fs.writeFileSync(filePath, content);

console.log('Syntax error fixed');
