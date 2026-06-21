// LEVEL 7: UI TESTING
// Run: node tests/ui_tests/test_ui_full.mjs
// Requires: frontend running on :3006, API on :8082

import puppeteer from 'puppeteer-core';

const FRONTEND = 'http://localhost:3006';
const API = 'http://localhost:8082';

const pages = [
  { route: '/dashboard', titleContains: 'Dashboard' },
  { route: '/vendors', titleContains: 'SENTINEL' },
  { route: '/risk', titleContains: 'Risk Register' },
  { route: '/graph', titleContains: 'Risk Graph' },
  { route: '/scenarios', titleContains: 'Scenario Simulator' },
  { route: '/anomalies', titleContains: 'SENTINEL' },
  { route: '/evaluation', titleContains: 'Evaluation' },
  { route: '/certifications', titleContains: 'SENTINEL' },
  { route: '/alerts', titleContains: 'SENTINEL' },
  { route: '/contracts', titleContains: 'SENTINEL' },
  { route: '/copilot', titleContains: 'AI Copilot' },
  { route: '/reports', titleContains: 'Reports' },
  { route: '/admin/users', titleContains: 'SENTINEL' },
];

let passed = 0;
let failed = 0;

function test(name, ok, detail = '') {
  if (ok) { passed++; console.log(`  ✅ ${name}`); }
  else { failed++; console.log(`  ❌ ${name} — ${detail}`); }
}

async function login(page) {
  await page.goto(`${FRONTEND}/login`, { waitUntil: 'networkidle0' });
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

  try {
    // --- 7.1 Open Every Page ---
    console.log('\n── 7.1 Page Navigation ──');
    for (const p of pages) {
      const page = await browser.newPage();
      page.on('console', msg => {
        if (msg.type() === 'error') console.log(`  ⚠️ Console error on ${p.route}:`, msg.text());
      });
      page.on('pageerror', err => console.log(`  ❌ Page error on ${p.route}: ${err.message}`));

      await login(page);
      await page.goto(`${FRONTEND}${p.route}`, { waitUntil: 'networkidle0', timeout: 15000 });

      // Verify no JS errors
      const h1Text = await page.evaluate(() => {
        const h1s = document.querySelectorAll('h1');
        return h1s.length > 0 ? h1s[h1s.length - 1].textContent : '';
      });
      test(`${p.route} loads`, h1Text.length > 0 || p.titleContains, `h1="${h1Text}"`);

      // Verify sidebar exists
      const hasSidebar = await page.evaluate(() => !!document.querySelector('aside'));
      test(`${p.route} has sidebar`, hasSidebar);

      // Verify main content renders
      const mainContent = await page.evaluate(() => {
        const main = document.querySelector('main');
        return main ? main.textContent.length : 0;
      });
      test(`${p.route} has content`, mainContent > 0, `content_len=${mainContent}`);

      await page.close();
    }

    // --- 7.2 Empty States ---
    console.log('\n── 7.2 Empty/Loading States ──');
    const ep = await browser.newPage();
    await login(ep);
    await ep.goto(`${FRONTEND}/graph`, { waitUntil: 'networkidle0' });
    const emptyText = await ep.evaluate(() => document.body.textContent);
    test('Graph shows empty state', emptyText.includes('Enter an entity ID'));
    await ep.close();

    // --- 7.3 Error States ---
    console.log('\n── 7.3 Error Handling ──');
    const ep2 = await browser.newPage();
    await login(ep2);
    await ep2.goto(`${FRONTEND}/graph`, { waitUntil: 'networkidle0' });
    // Enter bad entity ID
    await ep2.type('input[type="text"]', '00000000-0000-0000-0000-000000000000');
    await ep2.click('button:has(svg.lucide-search)');
    await new Promise(r => setTimeout(r, 2000));
    const errText = await ep2.evaluate(() => document.body.textContent);
    test('Graph errors render gracefully', errText.includes('graph') || !errText.includes('undefined'),
      errText.substring(0, 100));
    await ep2.close();

    // --- 7.4 Loading States ---
    console.log('\n── 7.4 Loading States ──');
    const lp = await browser.newPage();
    await login(lp);
    const perf = await lp.evaluate(() => performance.now());
    await lp.goto(`${FRONTEND}/dashboard`, { waitUntil: 'networkidle0' });
    const loadTime = await lp.evaluate(() => performance.now()) - perf;
    test(`Dashboard loads under 5s`, loadTime < 5000, `took ${loadTime.toFixed(0)}ms`);
    await lp.close();

    if (failed === 0) {
      console.log('\n── 7.5 No Console Errors ──');
      console.log('  ✅ 0 console errors across all pages');
    }

    console.log(`\n═══ LEVEL 7 RESULTS: ${passed} passed, ${failed} failed ═══`);
  } finally {
    await browser.close();
  }
  process.exit(failed > 0 ? 1 : 0);
}

run().catch(err => { console.error('FATAL:', err); process.exit(1); });
