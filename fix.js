const fs = require('fs');
const cards = JSON.parse(fs.readFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', 'utf8'));

// Replace all images with tiny placeholder
const placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="250" height="350"%3E%3Crect width="250" height="350" rx="12" fill="%232a2a4a"/%3E%3Ctext x="125" y="180" text-anchor="middle" fill="%23fff" font-size="14"%3ECard%3C/text%3E%3C/svg%3E';

for (const card of Object.values(cards)) {
  card.face.front.image = placeholder;
}

// Pretty print
fs.writeFileSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json', JSON.stringify(cards, null, 2), 'utf8');
console.log('File size:', fs.statSync('C:/Users/layja/obsidian/worldbuilding/card-game/tcg-arena/cards.json').size, 'bytes');
