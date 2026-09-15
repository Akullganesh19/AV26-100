const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 1024 } });
  const page = await context.newPage();
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(2000);

  // Tab sequentially through form
  await page.keyboard.press('Tab');
  await page.waitForTimeout(500);

  // Go to Calculator section
  await page.evaluate(() => {
    document.getElementById('calculator-section').scrollIntoView();
  });
  await page.waitForTimeout(1000);

  // Tab a few times to get focus on buttons
  for(let i=0; i<3; i++) {
     await page.keyboard.press('Tab');
     await page.waitForTimeout(500);
  }

  await page.screenshot({ path: '/home/jules/verification/screenshots/calculator_focus.png', fullPage: false });
  await context.close();
  await browser.close();
})();
