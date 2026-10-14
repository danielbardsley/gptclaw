import assert from 'node:assert/strict';
import test from 'node:test';
import jsQR from 'jsqr';
import { localQr } from '../lib/local-qr.ts';

function pixels(size:number,modules:Uint8Array):{data:Uint8ClampedArray;extent:number} {
  const scale=6;const extent=(size+8)*scale;
  const data=new Uint8ClampedArray(extent*extent*4);data.fill(255);
  for (let y=0;y<size;y++) for (let x=0;x<size;x++) if (modules[y*size+x]) {
    for (let dy=0;dy<scale;dy++) for (let dx=0;dx<scale;dx++) {
      const i=(((y+4)*scale+dy)*extent+(x+4)*scale+dx)*4;
      data[i]=data[i+1]=data[i+2]=0;
    }
  }
  return {data,extent};
}

test('independent decoder recovers complete synthetic session URLs including nonce',()=>{
  for (const port of [8443,8444]) for (const generation of ['a'.repeat(32),'f'.repeat(32)]) {
    const payload=`exps://forge-dev.example.ts.net:${port}/?gptclawSession=${generation}`;
    const {size,modules}=localQr(payload);const image=pixels(size,modules);
    assert.equal(jsQR(image.data,image.extent,image.extent)?.data,payload);
  }
});
test('small and maximum bounded ASCII payloads decode exactly',()=>{
  for (const payload of ['x','x'.repeat(512)]) {
    const {size,modules}=localQr(payload);const image=pixels(size,modules);
    assert.equal(jsQR(image.data,image.extent,image.extent)?.data,payload);
  }
});
test('QR input and output remain bounded with no raw markup interpolation',()=>{
  for (const payload of ['', 'x'.repeat(513), 'contains space','line\nbreak','\u0000','\u007f','📱']) {
    assert.throws(()=>localQr(payload),/Invalid QR payload/);
  }
  const payload='<svg/onload=alert(1)>';
  const result=localQr(payload);
  assert.ok(result.svg.length<150000);assert.ok(!result.svg.includes(payload));
  assert.ok(!result.svg.includes('onload'));assert.ok(!result.svg.includes('<script'));
  assert.match(result.svg,/viewBox="0 0 [0-9]+ [0-9]+"/);
});
test('quiet zone and deterministic pure encoding use no network or external assets',()=>{
  const first=localQr('synthetic');const second=localQr('synthetic');
  assert.deepEqual(first.modules,second.modules);assert.equal(first.svg,second.svg);
  assert.ok(!first.svg.includes('href='));assert.ok(!first.svg.includes('<image'));
  assert.match(first.svg,/fill="white"/);assert.match(first.svg,/shape-rendering="crispEdges"/);
});
