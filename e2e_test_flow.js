const { chromium } = require('playwright');
const fs = require('fs');

async function runTest() {
    console.log('🚀 Starting Comprehensive E2E Test Flow...');
    
    const browser = await chromium.launch({ 
        headless: false, // Set to false to see the interaction
        args: ['--disable-web-security', '--allow-running-insecure-content'] 
    });
    
    // Create a persistent context with saved auth state
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 },
        storageState: 'playwright-auth.json',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    const page = await context.newPage();

    // Extensive Logging
    page.on('console', msg => console.log(`BROWSER_LOG [${msg.type()}]: ${msg.text()}`));
    page.on('requestfailed', request => console.log(`REQUEST_FAILED: ${request.method()} ${request.url()} - ${request.failure()?.errorText}`));
    page.on('response', response => {
        if (response.status() >= 400) console.log(`RESPONSE_ERROR: ${response.status()} ${response.url()}`);
    });

    try {
        // Phase 1: Landing Page
        console.log('--- Phase 1: Landing Page ---');
        await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
        console.log('Landing page loaded.');
        await page.screenshot({ path: '1_landing_page.png' });

        // Phase 2: Navigating to Plans
        console.log('--- Phase 2: Navigating to Plans ---');
        await page.goto('http://localhost:3000/onboarding/plans', { waitUntil: 'networkidle', timeout: 60000 });
        
        console.log('Current URL after navigation:', page.url());
        await page.screenshot({ path: '2_plans_check.png' });

        if (page.url().includes('/login')) {
            console.error('❌ Redirected to login. Session bypass failed.');
        }

        // Phase 3: Plan Selection
        console.log('--- Phase 3: Plan Selection ---');
        try {
            await page.waitForSelector('text=Ascent', { timeout: 20000 });
            console.log('Ascent plan card found.');
        } catch (e) {
            console.log('Ascent plan card not found. Printing text snippet...');
            const text = await page.innerText('body');
            console.log('Page Text Snippet:', text.slice(0, 500));
        }

        // Click the Ascent card
        console.log('Clicking Ascent plan...');
        await page.click('text=Ascent');
        
        await page.waitForTimeout(2000);
        await page.screenshot({ path: '3_plan_selected.png' });

        console.log('Clicking "Continue to Payment"...');
        const continueButton = page.locator('button:has-text("Continue to Payment")');
        await continueButton.waitFor({ state: 'visible' });
        await continueButton.click();

        // Check for "Unauthorized"
        await page.waitForTimeout(3000);
        const unauthorized = await page.getByText('Unauthorized').isVisible();
        if (unauthorized) {
            console.error('❌ STILL UNAUTHORIZED. Trying to inject localStorage manually...');
            const authData = JSON.parse(fs.readFileSync('playwright-auth.json', 'utf8'));
            const projectRef = 'vpwwzsanuyhpkvgorcnc';
            const sessionStr = authData.origins[0].localStorage[0].value;
            
            await page.evaluate(({ key, value }) => {
                localStorage.setItem(key, value);
            }, { key: `sb-${projectRef}-auth-token`, value: sessionStr });
            
            console.log('Injected localStorage. Retrying click...');
            await page.click('button:has-text("Continue to Payment")');
            await page.waitForTimeout(3000);
        }

        // Phase 4: Payment (PhonePe)
        console.log('--- Phase 4: Payment ---');
        try {
            await page.waitForURL('**/onboarding/payment**', { timeout: 30000 });
            console.log('On payment initiation page:', page.url());
        } catch (e) {
            console.log('Timed out waiting for payment URL. Current URL:', page.url());
        }
        await page.screenshot({ path: '4_payment_initiation.png' });

        const payButton = page.locator('button:has-text("Pay"), button:has-text("Proceed to Payment"), button:has-text("Pay Now")').first();
        if (await payButton.isVisible()) {
            console.log('Clicking Pay button...');
            await payButton.click();
            
            console.log('Waiting for PhonePe redirect...');
            await page.waitForTimeout(10000); 
            console.log('Current URL at payment stage:', page.url());
            await page.screenshot({ path: '5_phonepe_page.png' });

            if (page.url().includes('phonepe.com')) {
                console.log('✅ Successfully reached PhonePe payment page!');
            } else {
                console.log('Did not reach PhonePe. Current URL:', page.url());
            }
        } else {
            console.log('Pay button not visible.');
        }

        console.log('--- E2E Test reaching Phase 4 complete ---');

    } catch (error) {
        console.error('❌ Error during E2E flow:', error);
        await page.screenshot({ path: 'error_screenshot.png' });
    } finally {
        await page.waitForTimeout(5000);
        await browser.close();
    }
}

runTest();