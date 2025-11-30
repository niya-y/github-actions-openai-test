const fs = require('fs');
const path = require('path');

const source = 'C:\\Users\\MJ\\.gemini\\antigravity\\brain\\b78d8569-21eb-4dfd-a15a-9ee70e1de73a\\uploaded_image_1_1764151543596.png';
const dest1 = 'c:\\dev\\neulbomcare\\frontend\\my-app\\public\\assets\\logo_color.png';
const dest2 = 'c:\\dev\\neulbomcare\\frontend\\my-app\\public\\assets\\logo_heart.png';

try {
    console.log('Copying to ' + dest1);
    fs.copyFileSync(source, dest1);
    console.log('Success dest1');

    console.log('Copying to ' + dest2);
    fs.copyFileSync(source, dest2);
    console.log('Success dest2');
} catch (e) {
    console.error('Error:', e);
}
