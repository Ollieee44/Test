// Print report.html to Oyster-Project-Report.pdf with headless Chromium, with page numbers in the footer.
// usage: NODE_PATH=<dir with playwright-core> node print_report.js
const { chromium } = require('playwright-core'); const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage();
  await p.goto('file://' + path.join(__dirname, 'report.html')); await p.waitForTimeout(500);
  await p.pdf({ path: path.join(__dirname, 'Oyster-Project-Report.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font:7px Inter,sans-serif;color:#65586A;padding:0 15mm;display:flex;justify-content:space-between">'
      + '<span>Oyster Therapeutics &middot; project report</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>' });
  await b.close(); console.log('Oyster-Project-Report.pdf');
})();
