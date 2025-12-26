import * as icons from '@hugeicons/core-free-icons';

const iconNames = Object.keys(icons);
console.log('Total icons:', iconNames.length);

const find = (pattern) => {
    const regex = new RegExp(pattern, 'i');
    const matches = iconNames.filter(n => regex.test(n));
    console.log(`${pattern}:`, matches.slice(0, 5));
};

find('Flash');
find('Energy');
find('Lightning');
find('Home');
find('Layer');
find('UserGroup');
find('Megaphone');
find('Dashboard');
find('Layout');
find('Sparkle');
find('Package');
find('Box');
find('Setting');
find('Arrow');
find('Plus');
