/* 검증용 초경량 정적 서버 — public/ 을 잠깐 띄웠다 닫는다 */
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', 'public');
const TYPE = { '.html':'text/html; charset=utf-8', '.json':'application/json', '.js':'text/javascript' };

function start(port = 8788) {
  const srv = http.createServer((req, res) => {
    const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html');
    if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end('nope'); }
    res.writeHead(200, { 'Content-Type': TYPE[path.extname(f)] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(res);
  });
  return new Promise(ok => srv.listen(port, () => ok({ srv, url: `http://localhost:${port}` })));
}
module.exports = { start };
