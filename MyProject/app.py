import os
import hashlib
import sqlite3
import uuid
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, render_template
from PIL import Image

# ─── Flask и папки ────────────────────────────────────────────────────────────
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ─── SQLite ───────────────────────────────────────────────────────────────────
DB_PATH = "conversions.db"


def get_db():
    """Открывает соединение; row_factory даёт доступ к столбцам по имени."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Создаёт таблицу при первом запуске.
    Поле expires_at — новое: момент, после которого запись/файл удаляются.
    """
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                sha256     TEXT    NOT NULL,
                target_fmt TEXT    NOT NULL,
                orig_name  TEXT    NOT NULL,
                out_file   TEXT    NOT NULL,
                created_at TEXT    NOT NULL,
                expires_at TEXT    NOT NULL,
                cache_hit  INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


# ─── Утилиты ──────────────────────────────────────────────────────────────────

def compute_sha256(path: str) -> str:
    """Побайтовое хеширование блоками 8 КБ — не нагружает RAM на больших файлах."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now().isoformat()


def expires_iso() -> str:
    """Время жизни файла: текущий момент + 24 часа."""
    return (datetime.now() + timedelta(hours=24)).isoformat()


def unique_name(ext: str) -> str:
    """UUID-имя для хранения на диске — исключает коллизии."""
    return f"{uuid.uuid4().hex}.{ext}"


def make_download_name(orig_name: str, target_fmt: str) -> str:
    """
    photo.png  +  jpg  →  photo.jpg
    Берём имя без расширения и добавляем новое.
    Это имя пользователь увидит при скачивании.
    """
    base = os.path.splitext(orig_name)[0]
    return f"{base}.{target_fmt}"


def lookup_cache(sha256: str, target_fmt: str):
    """
    Ищет в БД незаэкспайренную запись с тем же хешем и форматом.
    Условие expires_at > now() гарантирует, что файл ещё существует.
    """
    with get_db() as conn:
        row = conn.execute(
            """SELECT * FROM conversions
               WHERE sha256=? AND target_fmt=? AND expires_at > ?
               ORDER BY id DESC LIMIT 1""",
            (sha256, target_fmt, now_iso())
        ).fetchone()
    return row


def save_record(sha256, target_fmt, orig_name, out_file, cache_hit=0):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO conversions
               (sha256, target_fmt, orig_name, out_file, created_at, expires_at, cache_hit)
               VALUES (?,?,?,?,?,?,?)""",
            (sha256, target_fmt, orig_name, out_file,
             now_iso(), expires_iso(), cache_hit)
        )
        conn.commit()


# ─── Фоновая очистка ──────────────────────────────────────────────────────────

def cleanup_worker():
    """
    Фоновый поток (daemon): каждые 10 минут ищет в БД записи с истёкшим
    expires_at, удаляет файлы с диска, затем удаляет записи из БД.

    daemon=True означает, что поток автоматически завершится вместе
    с основным процессом Python — не нужно его явно останавливать.

    Порядок важен: сначала файл, потом запись. Если упадём между ними —
    в БД останется «мёртвая» запись без файла, но она не навредит:
    lookup_cache вернёт None (файла нет), конвертация произойдёт заново.
    """
    while True:
        try:
            with get_db() as conn:
                expired = conn.execute(
                    "SELECT id, out_file FROM conversions WHERE expires_at <= ?",
                    (now_iso(),)
                ).fetchall()

                for row in expired:
                    path = os.path.join(OUTPUT_FOLDER, row["out_file"])
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                    except OSError:
                        pass

                    conn.execute("DELETE FROM conversions WHERE id=?", (row["id"],))

                conn.commit()

        except Exception:
            pass

        time.sleep(600)


# ─── Конвертеры ───────────────────────────────────────────────────────────────

def convert_image(src: str, target_fmt: str) -> str:
    out_name = unique_name(target_fmt)
    out_path = os.path.join(OUTPUT_FOLDER, out_name)

    with Image.open(src) as img:
        if target_fmt in ("jpg", "jpeg") and img.mode in ("RGBA", "P", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = bg
        elif img.mode == "P":
            img = img.convert("RGBA")

        fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}
        img.save(out_path, format=fmt_map.get(target_fmt, target_fmt.upper()))

    return out_name


def convert_video_to_mp3(src: str) -> str:
    try:
        from moviepy.editor import VideoFileClip  # type: ignore
    except ImportError:
        raise RuntimeError("moviepy не установлен: pip install moviepy")

    out_name = unique_name("mp3")
    out_path = os.path.join(OUTPUT_FOLDER, out_name)
    clip = VideoFileClip(src)
    if clip.audio is None:
        clip.close()
        raise ValueError("В видеофайле нет аудиодорожки")
    clip.audio.write_audiofile(out_path, logger=None)
    clip.close()
    return out_name


def convert_office_to_pdf(src: str, orig_name: str) -> str:
    ext = os.path.splitext(orig_name)[1].lower()
    out_name = unique_name("pdf")
    out_path = os.path.join(OUTPUT_FOLDER, out_name)

    if ext == ".docx":
        try:
            from docx2pdf import convert as docx_convert
            docx_convert(src, out_path)
        except ImportError:
            _pdf_stub(out_path, f"Установите docx2pdf: pip install docx2pdf\nФайл: {orig_name}")
        except Exception as e:
            _pdf_stub(out_path, f"Ошибка конвертации DOCX: {e}")
    elif ext in (".xls", ".xlsx"):
        try:
            _excel_to_pdf(src, out_path)
        except Exception as e:
            _pdf_stub(out_path, f"Ошибка конвертации Excel: {e}")
    else:
        _pdf_stub(out_path, f"Конвертация .doc требует LibreOffice.\nФайл: {orig_name}")

    return out_name


def _excel_to_pdf(src: str, out_path: str):
    try:
        import openpyxl
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors
    except ImportError:
        raise RuntimeError("pip install openpyxl reportlab")

    wb = openpyxl.load_workbook(src, data_only=True)
    ws = wb.active
    data = [[str(c) if c is not None else "" for c in row]
            for row in ws.iter_rows(values_only=True)] or [["(пусто)"]]

    doc = SimpleDocTemplate(out_path, pagesize=A4)
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    doc.build([t])


def _pdf_stub(out_path: str, message: str):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        doc = SimpleDocTemplate(out_path, pagesize=A4)
        doc.build([Paragraph(message.replace("\n", "<br/>"), getSampleStyleSheet()["Normal"])])
    except ImportError:
        with open(out_path, "wb") as f:
            f.write(b"%PDF-1.4\n%%EOF")


# ─── Маршруты Flask ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    """
    POST /convert
    Принимает файл + target_fmt.
    Возвращает JSON {"token": "<uuid>", "filename": "photo.jpg"}
    вместо прямой отдачи файла. Клиент использует токен для скачивания
    через отдельный маршрут GET /download/<token>.
    Это позволяет показать кнопку «Скачать» вместо автоматической загрузки.
    """
    if "file" not in request.files:
        return jsonify({"error": "Файл не передан"}), 400

    file = request.files["file"]
    target_fmt = request.form.get("target_fmt", "").lower().strip()

    if not file.filename:
        return jsonify({"error": "Имя файла пустое"}), 400
    if not target_fmt:
        return jsonify({"error": "Не указан целевой формат"}), 400

    orig_name = file.filename
    src_ext   = os.path.splitext(orig_name)[1].lstrip(".") or "bin"
    tmp_name  = unique_name(src_ext)
    src_path  = os.path.join(UPLOAD_FOLDER, tmp_name)
    file.save(src_path)

    try:
        sha256 = compute_sha256(src_path)

        cached = lookup_cache(sha256, target_fmt)
        if cached:
            out_path = os.path.join(OUTPUT_FOLDER, cached["out_file"])
            if os.path.exists(out_path):
                save_record(sha256, target_fmt, orig_name,
                            cached["out_file"], cache_hit=1)
                dl_name = make_download_name(orig_name, target_fmt)
                return jsonify({
                    "token"    : cached["out_file"],
                    "filename" : dl_name,
                    "cache_hit": True
                })

        # Конвертация
        src_ext_dot = "." + os.path.splitext(orig_name)[1].lower().lstrip(".")
        image_exts  = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}

        if src_ext_dot in image_exts and target_fmt in ("jpg", "jpeg", "png", "webp"):
            out_file = convert_image(src_path, target_fmt)
        elif src_ext_dot == ".mp4" and target_fmt == "mp3":
            out_file = convert_video_to_mp3(src_path)
        elif src_ext_dot in (".doc", ".docx", ".xls", ".xlsx") and target_fmt == "pdf":
            out_file = convert_office_to_pdf(src_path, orig_name)
        else:
            return jsonify({"error": f"Конвертация {src_ext_dot} → {target_fmt} не поддерживается"}), 422

        save_record(sha256, target_fmt, orig_name, out_file, cache_hit=0)

        dl_name = make_download_name(orig_name, target_fmt)
        return jsonify({
            "token"    : out_file,
            "filename" : dl_name,
            "cache_hit": False
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(src_path):
            os.remove(src_path)


@app.route("/download/<token>")
def download(token: str):
    """
    GET /download/<token>
    Отдаёт готовый файл по его UUID-имени (токену).
    Параметр ?filename= задаёт имя, которое увидит пользователь при скачивании.

    Безопасность: os.path.basename(token) отрезает любые "../" — защита
    от path traversal атаки, когда злоумышленник пытается выйти за пределы
    папки outputs/ через имя вида "../../etc/passwd".
    """
    safe_token   = os.path.basename(token)
    dl_name      = request.args.get("filename", safe_token)
    dl_name      = os.path.basename(dl_name)

    out_path = os.path.join(OUTPUT_FOLDER, safe_token)
    if not os.path.exists(out_path):
        return jsonify({"error": "Файл не найден или истёк срок хранения"}), 404

    return send_file(out_path, as_attachment=True, download_name=dl_name)


@app.route("/history")
def history():
    """
    GET /history — записи за последние 24 часа (WHERE created_at > порог).
    Клиент больше не получит записи для удалённых/просроченных файлов.
    """
    threshold = (datetime.now() - timedelta(hours=24)).isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM conversions
               WHERE created_at > ?
               ORDER BY id DESC LIMIT 200""",
            (threshold,)
        ).fetchall()
    return jsonify([dict(row) for row in rows])


# ─── Точка входа ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()

    t = threading.Thread(target=cleanup_worker, daemon=True)
    t.start()

    app.run(debug=True)
