/**
 * Script to fix common TypeScript unused variable errors
 * Run with: node scripts/fix-unused-imports.js
 */

const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, '..', 'src');

// Common unused imports to remove
const unusedPatterns = [
  /^\s*TrendingUp,?\s*$/m,
  /^\s*BarChart3,?\s*$/m,
  /^\s*Users,?\s*$/m,
  /^\s*ArrowRight,?\s*$/m,
];

function processFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;

  // Remove unused import lines
  unusedPatterns.forEach(pattern => {
    if (pattern.test(content)) {
      content = content.replace(pattern, '');
      modified = true;
    }
  });

  // Clean up empty lines in import blocks
  content = content.replace(/from "lucide-react"\n\n+/g, 'from "lucide-react"\n');

  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Fixed: ${filePath}`);
  }
}

function walkDir(dir) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      walkDir(filePath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      processFile(filePath);
    }
  });
}

console.log('Fixing unused imports...');
walkDir(srcDir);
console.log('Done!');
