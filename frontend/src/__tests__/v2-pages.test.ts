/**
 * @jest-environment node
 */
import puppeteer from 'puppeteer-core';
import { beforeAll, afterAll, describe, test, expect } from '@jest/globals';

const FRONTEND_URL = 'http://localhost:3000';

let browser;

beforeAll(async () => {
  browser = await puppeteer.launch({ channel: 'chrome', headless: true });
});

afterAll(async () => {
  await browser.close();
});

async function login(page) {
  await page.goto(`${FRONTEND_URL}/login`, { waitUntil: 'networkidle0' });
  await page.waitForSelector('input[type="email"]');
  await page.type('input[type="email"]', 'admin@sentinel.ai');
  await page.type('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
}

describe('SENTINEL Frontend v2 Pages', () => {
  test('Sidebar shows new nav items', async () => {
    const page = await browser.newPage();
    await login(page);

    const sidebarText = await page.evaluate(() => document.querySelector('aside')?.textContent || '');
    expect(sidebarText).toContain('Risk Graph');
    expect(sidebarText).toContain('Scenario Simulator');
    expect(sidebarText).toContain('AI Copilot');
    await page.close();
  });

  test('Copilot v2 page loads and sends query', async () => {
    const page = await browser.newPage();
    await login(page);

    await page.goto(`${FRONTEND_URL}/copilot`, { waitUntil: 'networkidle0' });
    await page.waitForSelector('h1');
    const title = await page.$eval('h1', el => el.textContent);
    expect(title).toContain('AI Copilot');

    const body = await page.evaluate(() => document.body.textContent);
    expect(body).toContain('What should I focus on today?');
    expect(body).toContain('Generate board report');

    const input = await page.waitForSelector('input[type="text"]');
    await input.type('What should I focus on today?');
    await page.click('button:has(svg.lucide-send)');

    await page.waitForFunction(
      () => document.querySelectorAll('pre').length > 1,
      { timeout: 15000 }
    );
    const assistantText = await page.evaluate(() => {
      const pres = document.querySelectorAll('pre');
      return pres.length > 1 ? pres[pres.length - 1].textContent : '';
    });
    expect(assistantText.length).toBeGreaterThan(10);
    await page.close();
  });

  test('Scenario Simulator loads templates and runs scenario', async () => {
    const page = await browser.newPage();
    await login(page);

    await page.goto(`${FRONTEND_URL}/scenarios`, { waitUntil: 'networkidle0' });
    await page.waitForSelector('h1');
    const title = await page.$eval('h1', el => el.textContent);
    expect(title).toContain('Scenario Simulator');

    await page.waitForSelector('select:first-of-type option:not(:first-child)', { timeout: 10000 });
    await page.waitForSelector('select:nth-of-type(2) option:not(:first-child)', { timeout: 10000 });

    // get first non-placeholder option values
    const entityValue = await page.evaluate(() => {
      const s = document.querySelector('select:first-of-type');
      for (const opt of s.options) {
        if (opt.value) return opt.value;
      }
      return '';
    });
    if (!entityValue) {
      console.warn('No entities loaded — skipping scenario run test');
      await page.close();
      return;
    }

    const entitySelect = await page.waitForSelector('select:first-of-type');
    await entitySelect.select(entityValue);

    const scenarioSelect = await page.waitForSelector('select:nth-of-type(2)');
    await scenarioSelect.select('FAILURE');

    await page.click('button:has(svg)');

    await page.waitForFunction(
      () => document.body.textContent.includes('Blast Radius'),
      { timeout: 15000 }
    );
    const resultText = await page.evaluate(() => document.body.textContent);
    expect(resultText).toContain('Risk Delta');
    await page.close();
  });

  test('Graph page explores entity', async () => {
    const page = await browser.newPage();
    await login(page);

    await page.goto(`${FRONTEND_URL}/graph`, { waitUntil: 'networkidle0' });
    await page.waitForSelector('h1');
    const title = await page.$eval('h1', el => el.textContent);
    expect(title).toContain('Risk Graph');

    const body = await page.evaluate(() => document.body.textContent);
    expect(body).toContain('Enter an entity ID');

    // Fetch entity ID via page (browser context) using the stored token
    const entityId = await page.evaluate(async () => {
      const token = localStorage.getItem('access_token');
      if (!token) return '';
      const res = await fetch('http://localhost:8082/api/v2/entities?entity_type=VENDOR&size=1', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      return data?.data?.entities?.[0]?.entity_id || '';
    });

    if (entityId) {
      const input = await page.waitForSelector('input[type="text"]');
      await input.type(entityId);
      await page.click('button:has(svg.lucide-search)');

      await page.waitForFunction(
        () => document.querySelectorAll('.rounded-xl.border').length > 3,
        { timeout: 10000 }
      );
      const graphBody = await page.evaluate(() => document.body.textContent);
      expect(graphBody).toContain('VENDOR');
    } else {
      console.warn('No vendor entities — skipping graph exploration test');
    }
    await page.close();
  });
});
