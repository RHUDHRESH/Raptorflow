try {
    const icons = await import('@hugeicons/core-free-icons');
    const iconNames = Object.keys(icons);
    console.log('Total icons in core-free-icons:', iconNames.length);
    console.log('Flash/Energy:', iconNames.filter(n => n.match(/Flash|Energy|Lightning/i)));
    console.log('Home:', iconNames.filter(n => n.match(/Home/i)).slice(0, 5));
    console.log('Layers:', iconNames.filter(n => n.match(/Layer/i)).slice(0, 5));
    console.log('User:', iconNames.filter(n => n.match(/UserGroup/i)).slice(0, 5));
    console.log('Megaphone:', iconNames.filter(n => n.match(/Megaphone/i)).slice(0, 5));
    console.log('Dashboard:', iconNames.filter(n => n.match(/Dashboard|Layout/i)).slice(0, 5));
    console.log('Sparkles:', iconNames.filter(n => n.match(/Sparkle/i)).slice(0, 5));
    console.log('Box/Package:', iconNames.filter(n => n.match(/Package|Box/i)).slice(0, 5));
    console.log('Settings:', iconNames.filter(n => n.match(/Setting/i)).slice(0, 5));
    console.log('Arrow/Chevron:', iconNames.filter(n => n.match(/ArrowDown|Chevron/i)).slice(0, 5));
    console.log('Plus:', iconNames.filter(n => n.match(/Plus/i)).slice(0, 5));
} catch (e) {
    console.error('Error:', e.message);
}
