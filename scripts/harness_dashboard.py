#!/usr/bin/env python3
"""Harness Dashboard Realtime Server & Static Generator.

Usage:
  python3 scripts/harness_dashboard.py             # Sinh /tmp/harness_dashboard.html và khởi chạy server background trên 8765
  python3 scripts/harness_dashboard.py --serve     # Chạy foreground HTTP server trên cổng 8765
"""
import argparse
import http.server
import json
import os
import sys
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
from tools.floci_client import FlociHarnessDB

FIELDS = [
    "id", "type", "title", "state", "priority", "assigned_to",
    "assigned_to_profile", "iteration_path", "source", "updated_at"
]

HTML_TEMPLATE = """<!doctype html><meta charset=utf-8><title>Harness Dashboard (Realtime)</title>
<style>
body{font:13px system-ui;margin:16px;background:#fff;color:#222}
input,select{margin:0 6px 6px 0;padding:5px 8px;border:1px solid #ccc;border-radius:4px;font-size:12px}
input:focus,select:focus{border-color:#1890ff;outline:none}
table{border-collapse:collapse;width:100%;margin-top:8px}
th,td{border-bottom:1px solid #eee;padding:5px 8px;text-align:left;white-space:nowrap}
td:nth-child(3){white-space:normal;max-width:450px}
th{cursor:pointer;position:sticky;top:0;background:#f4f6f8;font-weight:600;color:#333;z-index:2}
tr:hover{background:#fafafa}
#hdr{display:flex;align-items:center;gap:12px;margin-bottom:8px}
#n{margin:6px 0;color:#666;font-size:12px}
.badge{padding:3px 8px;border-radius:12px;font-size:11px;font-weight:600;display:inline-flex;align-items:center;gap:4px}
.live{background:#e6f7ff;color:#096dd9;border:1px solid #91d5ff}
.err{background:#fff1f0;color:#cf1322;border:1px solid #ffa39e}
</style>
<div id=hdr>
  <h3 style="margin:0">Harness work items</h3>
  <span id=st class="badge live">● Realtime Live</span>
</div>
<div id=f></div>
<div id=n></div>
<table><thead><tr id=h></tr></thead><tbody id=b></tbody></table>
<script>
let D=__DATA__;
const C=__FIELDS__,sel={q:'',s:C[0],d:-1};
const filt=['type','state','priority','source','assigned_to_profile','iteration_path'];
const f=document.getElementById('f');

function initFilters(cur={}){
  const qVal = document.getElementById('q') ? document.getElementById('q').value : (cur.q || '');
  let html = `<input id=q placeholder="tìm id/title/assignee" size=30 value="${qVal.replace(/"/g, '&quot;')}">`;
  filt.forEach(k => {
    const vals = [...new Set(D.map(x=>x[k]||''))].sort();
    const selVal = cur[k] !== undefined ? cur[k] : (f.querySelector(`select[data-k="${k}"]`)?.value || '');
    html += `<select data-k="${k}"><option value="">${k}</option>` +
      vals.map(v => `<option value="${v.replace(/"/g, '&quot;')}" ${v===selVal?'selected':''}>${v}</option>`).join('') +
      '</select>';
  });
  f.innerHTML = html;
  f.oninput = r;
}

document.getElementById('h').innerHTML=C.map(k=>`<th data-k=${k}>${k}</th>`).join('');

function r(){
 const q=(document.getElementById('q')?.value || '').toLowerCase();
 const fs=[...f.querySelectorAll('select')].filter(s=>s.value);
 let a=D.filter(x=>(!q||(String(x.id)+' '+(x.title||'')+' '+(x.assigned_to||'')).toLowerCase().includes(q))&&fs.every(s=>(x[s.dataset.k]||'')==s.value));
 a.sort((x,y)=>(x[sel.s]>y[sel.s]?1:x[sel.s]<y[sel.s]?-1:0)*sel.d);
 document.getElementById('n').textContent=a.length+' / '+D.length;
 const b=document.getElementById('b');b.textContent='';
 for(const x of a.slice(0,1000)){
   const t=b.insertRow();
   for(const k of C) t.insertCell().textContent=x[k]??'';
 }
}

document.getElementById('h').onclick=e=>{
 const k=e.target.dataset.k;
 if(!k)return;
 sel.d=sel.s==k?-sel.d:1;
 sel.s=k;
 r();
};

initFilters();
r();

// Realtime Polling
let lastHash = '';
async function poll(){
  try{
    const origin = window.location.origin.includes('http') ? window.location.origin : 'http://127.0.0.1:8765';
    const res = await fetch(origin + '/api/work-items?t=' + Date.now());
    if(!res.ok) throw new Error('HTTP ' + res.status);
    const text = await res.text();
    if(text !== lastHash){
      lastHash = text;
      const data = JSON.parse(text);
      if(Array.isArray(data)){
        const cur = { q: document.getElementById('q')?.value || '' };
        f.querySelectorAll('select').forEach(s => { cur[s.dataset.k] = s.value; });
        D = data;
        initFilters(cur);
        r();
      }
    }
    const st = document.getElementById('st');
    if(st){
      st.className = 'badge live';
      st.textContent = '● Realtime Live (' + new Date().toLocaleTimeString() + ')';
    }
  }catch(e){
    const st = document.getElementById('st');
    if(st){
      st.className = 'badge err';
      st.textContent = '○ Offline (' + e.message + ')';
    }
  }
}
setInterval(poll, 2000);
</script>"""

_CACHE = {
    "data": [],
    "json_str": "[]",
    "last_fetch": 0.0
}
_LOCK = threading.Lock()


def get_cached_rows(force=False):
    now = time.time()
    with _LOCK:
        if force or (now - _CACHE["last_fetch"] > 1.5) or not _CACHE["data"]:
            try:
                items = FlociHarnessDB().list_work_items()
                rows = [{k: it.get(k) for k in FIELDS} for it in items]
                _CACHE["data"] = rows
                _CACHE["json_str"] = json.dumps(rows, ensure_ascii=False)
                _CACHE["last_fetch"] = now
            except Exception as e:
                print(f"[Dashboard Server] Fetch error: {e}", file=sys.stderr)
        return _CACHE["data"], _CACHE["json_str"]


def generate_html(out_path="/tmp/harness_dashboard.html"):
    rows, json_str = get_cached_rows(force=True)
    clean_data = json_str.replace("</", "<\\/")
    content = HTML_TEMPLATE.replace("__DATA__", clean_data).replace("__FIELDS__", json.dumps(FIELDS))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return len(rows)


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        url_path = self.path.split("?")[0]
        if url_path in ["/api/work-items", "/harness_data.json"]:
            _, json_str = get_cached_rows()
            body = json_str.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if url_path in ["/", "/harness_dashboard.html"]:
            rows, json_str = get_cached_rows()
            clean_data = json_str.replace("</", "<\\/")
            html = HTML_TEMPLATE.replace("__DATA__", clean_data).replace("__FIELDS__", json.dumps(FIELDS))
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        # Suppress routine log messages
        pass


def run_server(port=8765, host="0.0.0.0"):
    server_address = (host, port)
    httpd = http.server.ThreadingHTTPServer(server_address, DashboardHandler)
    print(f"Harness Realtime Server listening at http://127.0.0.1:{port}/harness_dashboard.html")
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Harness Dashboard Realtime Server & Static Generator")
    parser.add_argument("--serve", action="store_true", help="Chạy foreground HTTP server trên cổng 8765")
    parser.add_argument("--port", type=int, default=8765, help="Cổng server HTTP (default 8765)")
    parser.add_argument("out", nargs="?", default="/tmp/harness_dashboard.html", help="Đường dẫn file html output")
    args = parser.parse_args()

    count = generate_html(args.out)
    print(f"{count} items -> {args.out}")

    if args.serve:
        run_server(port=args.port)


if __name__ == "__main__":
    main()
