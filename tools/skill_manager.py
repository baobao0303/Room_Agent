#!/usr/bin/env python3
"""
tools/skill_manager.py - Centralized Skill Manager CLI & Web Dashboard Engine for Paseo SLPC.

Provides:
  1. Master Central Registry at `skills/`
  2. Multi-Target Automatic Sync (Global Claude, Paseo, Room_Agent, Paseo_Project, BMAD sub-rooms)
  3. CLI Commands: list, add, upload, sync, serve, doctor, remove
  4. Built-in Lightweight Zero-Dependency REST API & Web Dashboard Server
"""

import os
import re
import sys
import json
import shutil
import zipfile
import tarfile
import argparse
import base64
import mimetypes
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional, Tuple

# Workspace Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MASTER_REGISTRY = BASE_DIR / "skills"
WEB_DASHBOARD_FILE = BASE_DIR / "tools/web/skill_dashboard.html"

# Default Sync Targets
TARGET_DIRS = [
    Path(os.path.expanduser("~/.claude/skills")),
    Path(os.path.expanduser("~/.paseo/skills")),
    Path(os.path.expanduser("~/.hermes/skills")),
]
_local_agent_skills = BASE_DIR / ".agents" / "skills"
if _local_agent_skills.is_dir():
    TARGET_DIRS.append(_local_agent_skills)
_paseo_project_skills = Path(os.environ.get("PASEO_AGENTS_SKILLS", Path.home() / "Desktop" / "Paseo_Project" / ".agents" / "skills"))
if _paseo_project_skills.is_dir():
    TARGET_DIRS.append(_paseo_project_skills)


def ensure_dirs():
    """Ensure master registry and standard target directories exist."""
    MASTER_REGISTRY.mkdir(parents=True, exist_ok=True)
    for target in TARGET_DIRS:
        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass


def parse_skill_md(skill_file: Path) -> Dict[str, Any]:
    """Parse YAML frontmatter and content from SKILL.md."""
    if not skill_file.is_file():
        return {"name": skill_file.parent.name, "description": "", "content": ""}

    text = skill_file.read_text(encoding="utf-8", errors="replace")
    name = skill_file.parent.name
    desc = ""

    # Simple frontmatter parser
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if match:
        yaml_part = match.group(1)
        content_part = match.group(2)
        for line in yaml_part.splitlines():
            line = line.strip()
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("description:"):
                desc = line.split(":", 1)[1].strip().strip('"').strip("'")
        return {"name": name, "description": desc, "content": content_part.strip(), "raw": text}

    return {"name": name, "description": "", "content": text.strip(), "raw": text}


def get_all_skills() -> List[Dict[str, Any]]:
    """Scan Master Registry and all active target locations to list all skills."""
    ensure_dirs()
    skills_map: Dict[str, Dict[str, Any]] = {}

    def add_skill_entry(item_path: Path, src_name: str, src_type: str, is_master: bool = False):
        real_path = item_path.resolve() if item_path.is_symlink() else item_path
        skill_md = real_path / "SKILL.md"
        if not skill_md.exists():
            return
        skill_name = real_path.name
        if skill_name.startswith("."):
            return
        if skill_name not in skills_map:
            meta = parse_skill_md(skill_md)
            skills_map[skill_name] = {
                "name": skill_name,
                "description": meta.get("description", ""),
                "content": meta.get("raw", meta.get("content", "")),
                "source": src_name,
                "source_type": src_type,
                "path": str(real_path),
                "synced": is_master,
                "files_count": len(list(real_path.glob("**/*")))
            }

    # 1. Primary: Master Registry
    if MASTER_REGISTRY.is_dir():
        for item in MASTER_REGISTRY.iterdir():
            if item.is_dir():
                if (item / "SKILL.md").exists():
                    add_skill_entry(item, "Master Registry", "master", is_master=True)
                else:
                    for sub_item in item.iterdir():
                        if sub_item.is_dir() and (sub_item / "SKILL.md").exists():
                            add_skill_entry(sub_item, f"Master Registry ({item.name})", "master", is_master=True)

    # 2. Existing in Paseo Project .agents/skills
    proj_skills = _paseo_project_skills
    if proj_skills.is_dir():
        for item in proj_skills.iterdir():
            if item.is_dir():
                add_skill_entry(item, "Paseo Project", "project")

    # 3. Global ~/.claude/skills
    claude_skills = Path(os.path.expanduser("~/.claude/skills"))
    if claude_skills.is_dir():
        for item in claude_skills.iterdir():
            if item.is_dir():
                add_skill_entry(item, "Global Claude", "claude")

    # 4. Global ~/.paseo/skills
    paseo_skills = Path(os.path.expanduser("~/.paseo/skills"))
    if paseo_skills.is_dir():
        for item in paseo_skills.iterdir():
            if item.is_dir():
                add_skill_entry(item, "Paseo Platform", "paseo")

    # 5. Codex Skills ~/.codex/skills
    codex_skills = Path(os.path.expanduser("~/.codex/skills"))
    if codex_skills.is_dir():
        for item in codex_skills.iterdir():
            if item.is_dir():
                add_skill_entry(item, "Codex Skills", "codex")

    # 6. Gemini Skills ~/.gemini/config/skills
    gemini_skills = Path(os.path.expanduser("~/.gemini/config/skills"))
    if gemini_skills.is_dir():
        for item in gemini_skills.iterdir():
            if item.is_dir():
                add_skill_entry(item, "Gemini Config", "gemini")

    # 7. Gemini Plugins ~/.gemini/config/plugins/**/skills/*
    gemini_plugins = Path(os.path.expanduser("~/.gemini/config/plugins"))
    if gemini_plugins.is_dir():
        for sk_dir in gemini_plugins.glob("**/skills/*"):
            if sk_dir.is_dir():
                add_skill_entry(sk_dir, "Gemini Plugins", "gemini")

    # 8. Antigravity Builtin ~/.gemini/antigravity/builtin/skills
    ag_builtin = Path(os.path.expanduser("~/.gemini/antigravity/builtin/skills"))
    if ag_builtin.is_dir():
        for item in ag_builtin.iterdir():
            if item.is_dir():
                add_skill_entry(item, "Antigravity Builtin", "builtin")

    # Check sync status
    res = list(skills_map.values())
    res.sort(key=lambda x: x["name"])
    return res


def find_skill_in_master(skill_name: str) -> Optional[Path]:
    """Find skill directory in master registry across all profile subdirectories."""
    top = MASTER_REGISTRY / skill_name
    if top.is_dir() and (top / "SKILL.md").exists():
        return top
    for sub in MASTER_REGISTRY.iterdir():
        if sub.is_dir():
            nested = sub / skill_name
            if nested.is_dir() and (nested / "SKILL.md").exists():
                return nested
    return None


def sync_skills() -> Dict[str, Any]:
    """
    Consolidate all skills from Master Registry (`skills/`) and symlink to all target directories.
    Also cleans up broken symlinks in target directories.
    """
    ensure_dirs()
    synced_skills = []
    errors = []

    # Step 1: Build target directories list (only existing target directories)
    active_targets = [t for t in TARGET_DIRS if t.is_dir()]

    # Step 2: Clean up broken symlinks in active targets
    for target_dir in active_targets:
        try:
            for item in list(target_dir.iterdir()):
                if item.is_symlink() and not item.exists():
                    item.unlink(missing_ok=True)
        except Exception:
            pass

    # Step 3: Scan all master skills across profile directories (skills/<profile>/<skill>)
    all_master_skills = [s for s in MASTER_REGISTRY.rglob("*") if s.is_dir() and (s / "SKILL.md").exists()]

    for skill_dir in all_master_skills:
        skill_name = skill_dir.name
        skill_synced = True

        for target_dir in active_targets:
            target_link = target_dir / skill_name
            # If target is inside master registry itself, skip
            try:
                if target_link.exists() and target_link.resolve() == skill_dir.resolve():
                    continue
            except Exception:
                pass

            try:
                if target_link.is_symlink() or target_link.exists():
                    # Remove outdated or broken link
                    if target_link.is_symlink() or target_link.is_file():
                        target_link.unlink(missing_ok=True)
                    elif target_link.is_dir():
                        shutil.rmtree(target_link)

                target_link.symlink_to(skill_dir, target_is_directory=True)
            except Exception as e:
                skill_synced = False
                errors.append(f"Lỗi tạo link cho {skill_name} tại {target_dir}: {str(e)}")

        if skill_synced:
            synced_skills.append(skill_name)

    return {
        "success": len(errors) == 0,
        "synced_count": len(all_master_skills),
        "target_rooms_count": len(active_targets),
        "synced_skills": [s.name for s in all_master_skills],
        "errors": errors,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_harness_db():
    """Retrieve FlociHarnessDB instance with fallback."""
    try:
        if str(BASE_DIR) not in sys.path:
            sys.path.insert(0, str(BASE_DIR))
        try:
            from tools.floci_client import FlociHarnessDB
        except ImportError:
            from floci_client import FlociHarnessDB
        return FlociHarnessDB()
    except Exception as e:
        return None


def sync_skills_to_db() -> Dict[str, Any]:
    """Sync all discovered skills to DynamoDB/Local DB with an Inverted Index."""
    db = get_harness_db()
    if not db:
        return {"status": "error", "message": "Không thể kết nối FlociHarnessDB"}
    skills = get_all_skills()
    return db.sync_skills_index(skills)


def search_skills_db(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search skills on Database via Inverted Index without table scan."""
    db = get_harness_db()
    if not db:
        return []
    return db.search_skills(query, limit=limit)


def add_skill(name: str, description: str, content: str) -> Dict[str, Any]:
    """Create a new skill in Master Registry and trigger sync."""
    ensure_dirs()
    clean_name = re.sub(r"[^a-z0-9\-_]", "", name.lower().strip())
    if not clean_name:
        raise ValueError("Tên skill không hợp lệ (chỉ chấp nhận chữ thường, số, dấu - hoặc _).")

    dest = MASTER_REGISTRY / clean_name
    dest.mkdir(parents=True, exist_ok=True)

    header = f"---\nname: {clean_name}\ndescription: {description.strip()}\n---\n\n"
    full_content = header + content.strip() + "\n"

    (dest / "SKILL.md").write_text(full_content, encoding="utf-8")

    # Automatically sync
    sync_res = sync_skills()
    return {
        "success": True,
        "skill_name": clean_name,
        "path": str(dest),
        "sync_result": sync_res
    }


def upload_skill_archive(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """Extract a zip or tar archive and place it in Master Registry."""
    ensure_dirs()
    temp_extract = MASTER_REGISTRY / f"_temp_{int(datetime.now().timestamp())}"
    temp_extract.mkdir(parents=True, exist_ok=True)

    try:
        temp_file = temp_extract / filename
        temp_file.write_bytes(file_bytes)

        if zipfile.is_zipfile(temp_file):
            with zipfile.ZipFile(temp_file, "r") as z:
                z.extractall(temp_extract)
        elif tarfile.is_tarfile(temp_file):
            with tarfile.open(temp_file, "r:*") as t:
                t.extractall(temp_extract)
        elif filename.endswith(".md"):
            # Single SKILL.md uploaded
            skill_name = Path(filename).stem
            if skill_name.upper() == "SKILL":
                skill_name = f"skill-{int(datetime.now().timestamp())}"
            target_dir = MASTER_REGISTRY / skill_name
            target_dir.mkdir(parents=True, exist_ok=True)
            (target_dir / "SKILL.md").write_bytes(file_bytes)
            shutil.rmtree(temp_extract, ignore_errors=True)
            sync_skills()
            return {"success": True, "skill_name": skill_name}
        else:
            raise ValueError("Định dạng file không hỗ trợ (chỉ chấp nhận .zip, .tar.gz, .md).")

        temp_file.unlink(missing_ok=True)

        # Locate SKILL.md in extracted tree
        skill_files = list(temp_extract.glob("**/SKILL.md"))
        if not skill_files:
            # Check for any markdown file
            md_files = list(temp_extract.glob("**/*.md"))
            if md_files:
                skill_files = [md_files[0]]
            else:
                raise ValueError("Không tìm thấy tệp SKILL.md bên trong file nén tải lên.")

        chosen_skill_file = skill_files[0]
        skill_source_dir = chosen_skill_file.parent
        meta = parse_skill_md(chosen_skill_file)
        skill_name = meta.get("name") or skill_source_dir.name
        skill_name = re.sub(r"[^a-z0-9\-_]", "", skill_name.lower().strip())

        dest_dir = MASTER_REGISTRY / skill_name
        if dest_dir.exists():
            shutil.rmtree(dest_dir)

        shutil.copytree(skill_source_dir, dest_dir)
        shutil.rmtree(temp_extract, ignore_errors=True)

        # Trigger sync
        sync_skills()
        return {"success": True, "skill_name": skill_name, "path": str(dest_dir)}
    finally:
        if temp_extract.exists():
            shutil.rmtree(temp_extract, ignore_errors=True)


def delete_skill(name: str) -> Dict[str, Any]:
    """Delete a skill from Master Registry and unlink from all target rooms."""
    skill_dir = MASTER_REGISTRY / name
    if not skill_dir.is_dir():
        return {"success": False, "error": f"Skill '{name}' không tồn tại trong Master Registry."}

    shutil.rmtree(skill_dir)

    # Unlink across all targets
    for target in TARGET_DIRS:
        link = target / name
        if link.is_symlink() or link.is_file():
            link.unlink(missing_ok=True)
        elif link.is_dir():
            shutil.rmtree(link, ignore_errors=True)

    # Sub-rooms
    bmad_rooms = BASE_DIR / "bmad/rooms"
    if bmad_rooms.is_dir():
        for room in bmad_rooms.iterdir():
            link = room / ".claude/skills" / name
            if link.is_symlink() or link.is_file():
                link.unlink(missing_ok=True)

    return {"success": True, "deleted": name}


# ---------- HTTP SERVER & REST API HANDLER ----------

class SkillManagerApiHandler(BaseHTTPRequestHandler):
    def send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]

        # Serve Web Dashboard
        if path in ("/", "/index.html", "/skills"):
            if WEB_DASHBOARD_FILE.is_file():
                html = WEB_DASHBOARD_FILE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
                return
            else:
                self.send_error(404, "Dashboard HTML not found")
                return

        # API: List all skills
        if path == "/api/skills":
            skills = get_all_skills()
            self.send_json({"skills": skills, "total": len(skills)})
            return

        # API: Get single skill detail
        if path.startswith("/api/skills/"):
            skill_name = path[len("/api/skills/"):].strip("/")
            skill_dir = MASTER_REGISTRY / skill_name
            if not skill_dir.is_dir():
                # Check global
                skill_dir = Path(os.path.expanduser(f"~/.claude/skills/{skill_name}")).resolve()

            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                meta = parse_skill_md(skill_dir / "SKILL.md")
                files = [p.name for p in skill_dir.iterdir()]
                self.send_json({
                    "success": True,
                    "skill": {
                        "name": skill_name,
                        "description": meta.get("description", ""),
                        "content": meta.get("raw") or meta.get("content", ""),
                        "files": files,
                        "path": str(skill_dir)
                    }
                })
                return
            self.send_json({"success": False, "error": f"Skill '{skill_name}' không tìm thấy"}, 404)
            return

        self.send_error(404, "Endpoint not found")

    def do_POST(self):
        path = self.path.split("?")[0]

        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length) if length > 0 else b""

        # API: Sync skills
        if path == "/api/skills/sync":
            res = sync_skills()
            self.send_json(res)
            return

        # API: Create skill
        if path == "/api/skills/create":
            try:
                body = json.loads(post_data.decode("utf-8"))
                name = body.get("name", "")
                desc = body.get("description", "")
                content = body.get("content", "")
                res = add_skill(name, desc, content)
                self.send_json(res)
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 400)
            return

        # API: Upload skill archive
        if path == "/api/skills/upload":
            try:
                body = json.loads(post_data.decode("utf-8"))
                filename = body.get("filename", "skill.zip")
                b64_data = body.get("data", "")
                file_bytes = base64.b64decode(b64_data)
                res = upload_skill_archive(filename, file_bytes)
                self.send_json(res)
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 400)
            return

        self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        path = self.path.split("?")[0]
        if path.startswith("/api/skills/"):
            skill_name = path[len("/api/skills/"):].strip("/")
            res = delete_skill(skill_name)
            self.send_json(res)
            return
        self.send_error(404, "Endpoint not found")


def serve_dashboard(port: int = 5252, auto_open: bool = False):
    """Run local HTTP server serving Skill Manager Web Dashboard."""
    # Run sync on startup to guarantee all current skills are indexed
    sync_skills()

    server_address = ("", port)
    httpd = HTTPServer(server_address, SkillManagerApiHandler)
    url = f"http://localhost:{port}"

    print(f"🚀 [Skill Hub] Web Dashboard đang chạy tại: {url}")
    print(f"📁 Master Registry: {MASTER_REGISTRY}")
    print(f"Press Ctrl+C to stop.")

    if auto_open:
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 [Skill Hub] Đã dừng server.")


# ---------- CLI DISPATCHER ----------

def main():
    parser = argparse.ArgumentParser(description="Skill Manager CLI & Web Dashboard Engine for Paseo")
    subparsers = parser.add_subparsers(dest="command", help="Lệnh quản lý skill")

    # list
    p_list = subparsers.add_parser("list", help="Liệt kê toàn bộ skills trong hệ thống")
    p_list.add_argument("--json", action="store_true", help="Xuất kết quả JSON")

    # sync
    p_sync = subparsers.add_parser("sync", help="Đồng bộ toàn bộ skills sang các room và target directories")

    # add
    p_add = subparsers.add_parser("add", help="Thêm skill mới vào Master Registry")
    p_add.add_argument("--name", required=True, help="Tên skill (kebab-case)")
    p_add.add_argument("--desc", default="", help="Mô tả kỹ năng")
    p_add.add_argument("--content", default="", help="Nội dung SKILL.md hoặc đường dẫn tệp")

    # upload / import
    p_up = subparsers.add_parser("upload", help="Upload hoặc import skill từ file zip/tar hoặc thư mục")
    p_up.add_argument("path", help="Đường dẫn đến file .zip, .tar.gz hoặc thư mục chứa skill")

    # remove
    p_rm = subparsers.add_parser("remove", help="Xóa skill khỏi Registry và gỡ bỏ liên kết các phòng")
    p_rm.add_argument("name", help="Tên skill cần xóa")

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Kiểm tra toàn vẹn symlinks và cấu trúc skills")

    # serve
    p_serve = subparsers.add_parser("serve", help="Khởi chạy Web Dashboard trên browser")
    p_serve.add_argument("--port", type=int, default=5252, help="Cổng máy chủ (mặc định: 5252)")
    p_serve.add_argument("--open", action="store_true", help="Tự động mở trình duyệt")

    # sync-db
    p_syncdb = subparsers.add_parser("sync-db", help="Lập chỉ mục Inverted Index toàn bộ skills lên DynamoDB/Local DB")

    # search / query
    p_search = subparsers.add_parser("search", help="Tìm kiếm skill hiệu quả bằng Inverted Index trên DB (không ScanAll)")
    p_search.add_argument("query", help="Từ khóa hoặc chuỗi cần tìm kiếm")
    p_search.add_argument("--limit", type=int, default=10, help="Số lượng kết quả tối đa (mặc định: 10)")
    p_search.add_argument("--json", action="store_true", help="Xuất kết quả JSON")

    p_query = subparsers.add_parser("query", help="Alias của search - Query skill trên DB qua Inverted Index")
    p_query.add_argument("query", help="Từ khóa hoặc chuỗi cần tìm kiếm")
    p_query.add_argument("--limit", type=int, default=10, help="Số lượng kết quả tối đa (mặc định: 10)")
    p_query.add_argument("--json", action="store_true", help="Xuất kết quả JSON")

    args = parser.parse_args()

    if args.command == "list" or not args.command:
        skills = get_all_skills()
        if getattr(args, "json", False):
            print(json.dumps(skills, indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 80)
            print("🧰 DANH SÁCH SKILLS (SKILL HUB MASTER REGISTRY)")
            print("=" * 80)
            print(f"{'TÊN SKILL':<30} {'NGUỒN':<18} {'TRẠNG THÁI':<12} {'MÔ TẢ'}")
            print("-" * 80)
            for s in skills:
                status = "✅ Synced" if s.get("synced") else "🔄 Local"
                desc = (s.get("description") or "")[:40]
                print(f"{s['name']:<30} {s['source']:<18} {status:<12} {desc}")
            print("-" * 80)
            print(f"Tổng số: {len(skills)} skills. Dùng 'python3 tools/skill_manager.py sync' để đồng bộ.\n")

    elif args.command == "sync":
        print("⚡ Đang quét và đồng bộ kỹ năng tới tất cả các Room...")
        res = sync_skills()
        print(f"✅ Đã đồng bộ {res['synced_count']} skills sang {res['target_rooms_count']} phòng/workspaces!")
        if res["errors"]:
            print("⚠️ Cảnh báo lỗi:")
            for err in res["errors"]:
                print(f"  - {err}")
        db_res = sync_skills_to_db()
        if db_res.get("status") == "success":
            print(f"🗄️ Đã lập chỉ mục Inverted Index {db_res['indexed_skills']} skills ({db_res['unique_tokens']} tokens) lên Database ({db_res['backend']})!")

    elif args.command == "add":
        content = args.content
        if os.path.isfile(content):
            content = Path(content).read_text(encoding="utf-8")
        res = add_skill(args.name, args.desc, content)
        print(f"✅ Đã tạo skill: /{res['skill_name']} và đồng bộ sang tất cả các Room.")

    elif args.command == "upload":
        p = Path(args.path)
        if not p.exists():
            print(f"❌ Đường dẫn không tồn tại: {p}")
            sys.exit(1)
        if p.is_dir():
            dest = MASTER_REGISTRY / p.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(p, dest)
            sync_skills()
            print(f"✅ Đã nạp thư mục skill: /{p.name} vào Master Registry và đồng bộ xong.")
        else:
            data = p.read_bytes()
            res = upload_skill_archive(p.name, data)
            print(f"✅ Đã giải nén và nạp skill: /{res['skill_name']} và đồng bộ xong.")

    elif args.command == "remove":
        res = delete_skill(args.name)
        if res.get("success"):
            print(f"✅ Đã xóa skill: /{args.name}")
        else:
            print(f"❌ {res.get('error')}")

    elif args.command == "doctor":
        print("🩺 Đang kiểm tra sức khỏe hệ thống Skill...")
        skills = get_all_skills()
        broken_links = 0
        for target in TARGET_DIRS:
            if target.is_dir():
                for item in target.iterdir():
                    if item.is_symlink() and not item.exists():
                        print(f"⚠️ Phát hiện link gãy: {item} -> Đang xóa...")
                        item.unlink()
                        broken_links += 1
        print(f"✅ Kiểm tra hoàn tất. Đã sửa {broken_links} link gãy. Tổng số {len(skills)} skills hợp lệ.")

    elif args.command == "serve":
        serve_dashboard(port=args.port, auto_open=args.open)

    elif args.command == "sync-db":
        print("⚡ Đang quét và lập chỉ mục Inverted Index toàn bộ skills lên Database...")
        res = sync_skills_to_db()
        if res.get("status") == "success":
            print(f"✅ Đã lập chỉ mục {res['indexed_skills']} skills thành công!")
            print(f"🔑 Tổng số unique search tokens: {res['unique_tokens']}")
            print(f"🗄️ Backend lưu trữ: {res['backend']}")
        else:
            print(f"❌ Lỗi: {res.get('message')}")

    elif args.command in ("search", "query"):
        q = args.query.strip()
        if not q:
            print("⚠️ Vui lòng nhập từ khóa tìm kiếm!")
            sys.exit(1)

        results = search_skills_db(q, limit=args.limit)

        if getattr(args, "json", False):
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 95)
            print(f"🔍 KẾT QUẢ TÌM KIẾM SKILL TRÊN DB (INVERTED INDEX) CHO TỪ KHÓA: \"{q}\"")
            print("=" * 95)
            if not results:
                print(f"ℹ️ Không tìm thấy skill nào khớp với từ khóa \"{q}\".")
                print("Tip: Chạy 'python3 tools/skill_manager.py sync-db' để đảm bảo index DB được cập nhật.")
            else:
                print(f"{'#':<3} {'SCORE':<7} {'TÊN SKILL':<28} {'TOKENS KHỚP':<18} {'MÔ TẢ'}")
                print("-" * 95)
                for item in results:
                    rank = str(item.get("rank", 1))
                    score = str(item.get("score", 0.0))
                    name = item.get("name", "")[:26]
                    matched = ",".join(item.get("matched_tokens", []))[:16]
                    desc = (item.get("description") or "").replace("\n", " ")[:38]
                    print(f"{rank:<3} {score:<7} {name:<28} {matched:<18} {desc}")
                print("-" * 95)
                print(f"Tìm thấy {len(results)} kết quả phù hợp (Truy vấn phân vùng O(1), không Scan toàn bảng).\n")


if __name__ == "__main__":
    main()
