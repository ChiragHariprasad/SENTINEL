import puppeteer from 'puppeteer-core';

const FRONTEND_URL = 'http://localhost:3006';
const API_URL = 'http://localhost:8082';

async function login(page) {
  await page.goto(`${FRONTEND_URL}/login`, { waitUntil: 'networkidle0' });
  await page.waitForSelector('input[type="email"]');
  await page.type('input[type="email"]', 'admin@sentinel.ai');
  await page.type('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForNetworkIdle({ timeout: 10000 });
}

async function run() {
  const browser = await puppeteer.launch({
    executablePath: '/usr/lib64/chromium-browser/chromium-browser.sh',
    headless: true,
  });
  const errors = [];

  try {
    // Test 1: Sidebar
    console.log('1. Sidebar nav items...');
    const p1 = await browser.newPage();
    await login(p1);
    const sidebarText = await p1.evaluate(() => document.querySelector('aside')?.textContent || '');
    if (!sidebarText.includes('Risk Graph')) throw new Error('Missing Risk Graph in sidebar');
    if (!sidebarText.includes('Scenario Simulator')) throw new Error('Missing Scenario Simulator in sidebar');
    if (!sidebarText.includes('AI Copilot')) throw new Error('Missing AI Copilot in sidebar');
    console.log('   ✅ Sidebar has all v2 nav items');
    await p1.close();

    // Test 2: Copilot v2
    console.log('2. Copilot v2 query...');
    const p2 = await browser.newPage();
    await login(p2);
    await p2.goto(`${FRONTEND_URL}/copilot`, { waitUntil: 'networkidle0' });
    await p2.waitForFunction(() => {
      const h1s = document.querySelectorAll('h1');
      return h1s.length >= 2 && h1s[1].textContent.includes('AI Copilot');
    });
    const title2 = await p2.evaluate(() => document.querySelectorAll('h1')[1].textContent);
    if (!title2.includes('AI Copilot')) throw new Error('Copilot page title wrong');
    const body2 = await p2.evaluate(() => document.body.textContent);
    if (!body2.includes('What should I focus on today?')) throw new Error('Missing suggestion chips');
    const input2 = await p2.waitForSelector('input[type="text"]');
    await input2.type('What should I focus on today?');
    await p2.click('button:has(svg.lucide-send)');
    await p2.waitForFunction(
      () => document.querySelectorAll('pre').length > 1,
      { timeout: 15000 }
    );
    const answer2 = await p2.evaluate(() => {
      const pres = document.querySelectorAll('pre');
      return pres[pres.length - 1].textContent;
    });
    if (answer2.length < 10) throw new Error('Copilot response too short');
    console.log(`   ✅ Copilot responded (${answer2.length} chars)`);
    await p2.close();

    // Test 3: Scenario Simulator
    console.log('3. Scenario Simulator...');
    const p3 = await browser.newPage();
    await login(p3);
    await p3.goto(`${FRONTEND_URL}/scenarios`, { waitUntil: 'networkidle0' });
    await p3.waitForFunction(() => {
      const h1s = document.querySelectorAll('h1');
      return h1s.length >= 2 && h1s[1].textContent.includes('Scenario Simulator');
    });
    const title3 = await p3.evaluate(() => document.querySelectorAll('h1')[1].textContent);
    if (!title3.includes('Scenario Simulator')) throw new Error('Scenario page title wrong');

    // Wait for all selects to have options
    await p3.waitForFunction(() => {
      const selects = document.querySelectorAll('select');
      return selects.length >= 2 &&
        selects[0].options.length > 1 &&
        selects[1].options.length > 0;
    }, { timeout: 15000 });

    const entityValue = await p3.evaluate(() => {
      const s = document.querySelector('select:first-of-type');
      for (const opt of s.options) {
        if (opt.value) return opt.value;
      }
      return '';
    });
    if (!entityValue) throw new Error('No entities loaded in selector');

    // Select the first entity and FAILURE scenario using evaluate
    await p3.evaluate((val) => {
      const s = document.querySelector('select');
      s.value = val;
      s.dispatchEvent(new Event('change', { bubbles: true }));
    }, entityValue);
    await p3.evaluate(() => {
      const s = document.querySelectorAll('select')[1];
      s.value = 'FAILURE';
      s.dispatchEvent(new Event('change', { bubbles: true }));
    });
    // Click the Run Simulation button (the only button with text)
    await p3.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const runBtn = buttons.find(b => b.textContent.includes('Run Simulation'));
      if (runBtn) runBtn.click();
    });

    await p3.waitForFunction(
      () => document.body.textContent.includes('Blast Radius'),
      { timeout: 15000 }
    );
    const result3 = await p3.evaluate(() => document.body.textContent);
    if (!result3.includes('Risk Delta')) throw new Error('Missing Risk Delta in results');
    console.log('   ✅ Scenario simulation returned results');
    await p3.close();

    // Test 4: Graph page
    console.log('4. Risk Graph page...');
    const p4 = await browser.newPage();
    await login(p4);
    await p4.goto(`${FRONTEND_URL}/graph`, { waitUntil: 'networkidle0' });
    await p4.waitForFunction(() => {
      const h1s = document.querySelectorAll('h1');
      return h1s.length >= 2 && h1s[1].textContent.includes('Risk Graph');
    });
    const title4 = await p4.evaluate(() => document.querySelectorAll('h1')[1].textContent);
    if (!title4.includes('Risk Graph')) throw new Error('Graph page title wrong');

    const entityId = await p4.evaluate(async (apiUrl) => {
      const token = localStorage.getItem('access_token');
      if (!token) return '';
      const res = await fetch(`${apiUrl}/api/v2/entities?entity_type=VENDOR&size=1`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      return data?.data?.entities?.[0]?.entity_id || '';
    }, API_URL);

    if (entityId) {
      const input4 = await p4.waitForSelector('input[type="text"]');
      await input4.type(entityId);
      await p4.click('button:has(svg.lucide-search)');
      await p4.waitForFunction(
        () => document.querySelectorAll('.rounded-xl.border').length > 3,
        { timeout: 10000 }
      );
      const graphBody = await p4.evaluate(() => document.body.textContent);
      if (!graphBody.includes('VENDOR')) throw new Error('Graph results missing VENDOR');
      console.log(`   ✅ Graph loaded entity ${entityId.slice(0, 12)}...`);
    } else {
      console.log('   ⚠️ No vendor entities, skipping graph exploration');
    }
    await p4.close();

    console.log('\n✅ All v2 frontend tests passed!');
  } catch (err) {
    console.error(`\n❌ Test failed: ${err.message}`);
    errors.push(err.message);
  } finally {
    await browser.close();
  }

  if (errors.length > 0) process.exit(1);
}

run().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
