const fs = require('fs');
const path = require('path');

const targetDirs = [
    'c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\src\\app',
    'c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\src\\components'
];

const featureComponents = ['AgentChat', 'AgentManagement', 'InteractiveHero', 'WorkflowBuilder'];
const uiComponents = {
    'Button': 'Button_old',
    'Card': 'Card_old',
    'CustomCursor': 'CustomCursor_old',
    'Input': 'Input_old',
    'Magnetic': 'Magnetic',
    'Preloader': 'Preloader_old',
    'RevealText': 'RevealText',
    'ScrambleText': 'ScrambleText',
    'SpotlightCard': 'SpotlightCard'
};

function walk(dir, callback) {
    if (!fs.existsSync(dir)) return;
    fs.readdirSync(dir).forEach(f => {
        let dirPath = path.join(dir, f);
        if (dirPath.includes('node_modules') || dirPath.includes('.next')) return;
        let isDirectory = fs.statSync(dirPath).isDirectory();
        isDirectory ? walk(dirPath, callback) : callback(path.join(dir, f));
    });
}

let modified = 0;

targetDirs.forEach(dir => {
    walk(dir, function (filePath) {
        if (!(filePath.endsWith('.tsx') || filePath.endsWith('.ts') || filePath.endsWith('.jsx'))) return;
        let content = fs.readFileSync(filePath, 'utf8');
        let originalContent = content;

        featureComponents.forEach(comp => {
            content = content.replace(new RegExp(`"@/components/${comp}"`, 'g'), `"@/components/features/${comp}"`);
            content = content.replace(new RegExp(`'@/components/${comp}'`, 'g'), `'@/components/features/${comp}'`);
            content = content.replace(new RegExp(`"\\.\\./components/${comp}"`, 'g'), `"../components/features/${comp}"`);
            content = content.replace(new RegExp(`"\\.\\./\\.\\./components/${comp}"`, 'g'), `"../../components/features/${comp}"`);
        });

        Object.entries(uiComponents).forEach(([comp, newName]) => {
            content = content.replace(new RegExp(`"@/components/${comp}"`, 'g'), `"@/components/ui/${newName}"`);
            content = content.replace(new RegExp(`'@/components/${comp}'`, 'g'), `'@/components/ui/${newName}'`);
            content = content.replace(new RegExp(`"\\.\\./components/${comp}"`, 'g'), `"../components/ui/${newName}"`);
            content = content.replace(new RegExp(`"\\.\\./\\.\\./components/${comp}"`, 'g'), `"../../components/ui/${newName}"`);
        });

        if (content !== originalContent) {
            fs.writeFileSync(filePath, content, 'utf8');
            modified++;
            console.log(`Updated ${filePath}`);
        }
    });
});

console.log(`Updated ${modified} frontend files.`);
