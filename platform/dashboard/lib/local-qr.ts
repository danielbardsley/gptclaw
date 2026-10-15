import { toQR } from 'toqr';

// Pure local encoding. Callers must separately validate current launch eligibility.
// No URLs are fetched, and no raw payload text enters generated SVG markup.
export function localQr(payload:string):{size:number; modules:Uint8Array; svg:string} {
  if (typeof payload !== 'string' || payload.length < 1 || payload.length > 512
      || !/^[\x21-\x7e]+$/.test(payload)) throw new Error('Invalid QR payload');
  const modules=toQR(payload,0);
  const size=Math.sqrt(modules.length);
  if (!Number.isInteger(size) || size < 21 || size > 97 || (size-21)%4 !== 0
      || modules.some(value=>value !== 0 && value !== 1)) throw new Error('Invalid QR matrix');
  const extent=size+8;
  let path='';
  for (let y=0;y<size;y++) for (let x=0;x<size;x++) {
    if (modules[y*size+x]) path+=`M${x+4} ${y+4}h1v1h-1z`;
  }
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${extent} ${extent}" width="320" height="320" shape-rendering="crispEdges"><rect width="${extent}" height="${extent}" fill="white"/><path d="${path}" fill="black"/></svg>`;
  if (svg.length > 150000) throw new Error('QR output exceeds bound');
  return {size,modules,svg};
}
