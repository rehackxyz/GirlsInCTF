const puppeteer = require('puppeteer');
const flag = 'GCTF25{f0rg0r_70_3nc0d3_0r_41_d3c0d3_17}';

(async () => {
    let browser;
    try {
        console.log('Launching Puppeteer...');
        browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });
        const page = await browser.newPage();
        console.log('Puppeteer launched, new page created.');

        // Use URL-based cookie to avoid domain serialization issues
        await page.setCookie({
            name: 'flag',
            value: String(flag),
            url: 'http://localhost:5000/',
            httpOnly: false,
            secure: false
        });
        console.log('Flag cookie set.');

        const url = 'http://localhost:5000/render_conversations';
        console.log(`Navigating to ${url}`);
        await page.goto(url, {
            waitUntil: 'networkidle0'
        });
        console.log('Page loaded successfully.');

        const content = await page.content();
        console.log('Successfully fetched page content.');

    } catch (error) {
        console.error('Error during puppeteer execution:', error);
        process.exit(1);
    } finally {
        if (browser) {
            await browser.close();
            console.log('Browser closed.');
        }
    }
})();