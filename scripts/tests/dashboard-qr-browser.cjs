const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('playwright-core');
const jsQR=require('/dashboard-modules/jsqr');
(async()=>{
 const svg=fs.readFileSync('/qr/code.svg');
 assert.ok(svg.length<=150000);
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try {
  const page=await browser.newPage();
  const pixels=await page.evaluate(async encoded=>{
   const image=new Image();
   await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=reject;
     image.src='data:image/svg+xml;base64,'+encoded;});
   const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;
   const context=canvas.getContext('2d');context.drawImage(image,0,0);
   return {width:canvas.width,height:canvas.height,data:Array.from(context.getImageData(0,0,canvas.width,canvas.height).data)};
  },svg.toString('base64'));
  assert.equal(pixels.width,320);assert.equal(pixels.height,320);
  const decoded=jsQR(new Uint8ClampedArray(pixels.data),pixels.width,pixels.height);
  assert.equal(decoded?.data,'exps://forge-dev.example.ts.net:8443/?gptclawSession='+'a'.repeat(32));
  console.log('PASS: actual locally rendered SVG decodes to the complete synthetic payload; no phone or external service used');
 } finally {await browser.close();}
})().catch(()=>{console.error('QR SVG browser/decode check failed');process.exit(1);});
