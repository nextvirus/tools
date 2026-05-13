"""可选模块探测：真实 import，结果缓存；失败原因单独记录便于容错与排错。

探测在后台线程执行；`probe_optional_modules_blocking` 对 pdf / photo / meeting 三路并行 try import，
总耗时接近「最慢一路」而非三者之和（受 Python import 锁与扩展实现影响，不保证严格并行）。
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

_probe: OptionalModulesProbe | None = None


@dataclass(frozen=True)
class OptionalModulesProbe:
    """各可选模块是否已通过 import 自检；errors 仅含失败项。"""

    pdf: bool
    photo: bool
    meeting: bool
    errors: dict[str, BaseException]


def try_import_pdf() -> tuple[bool, BaseException | None]:
    try:
        import fitz  # noqa: F401  # PyMuPDF
        return True, None
    except Exception as e:
        return False, e


def try_import_photo() -> tuple[bool, BaseException | None]:
    try:
        import onnxruntime  # noqa: F401
        import rembg  # noqa: F401
        return True, None
    except Exception as e:
        return False, e


def try_import_meeting() -> tuple[bool, BaseException | None]:
    try:
        import sounddevice  # noqa: F401
        import vosk  # noqa: F401
        return True, None
    except Exception as e:
        return False, e


def probe_optional_modules_blocking() -> OptionalModulesProbe:
    """并行探测三路模块；供脚本/基准或单线程合并结果使用。"""
    global _probe
    errors: dict[str, BaseException] = {}
    pdf_ok = photo_ok = meeting_ok = False
    with ThreadPoolExecutor(max_workers=3) as ex:
        future_map = {
            ex.submit(try_import_pdf): "pdf",
            ex.submit(try_import_photo): "photo",
            ex.submit(try_import_meeting): "meeting",
        }
        for fut in as_completed(future_map):
            key = future_map[fut]
            ok, err = fut.result()
            if key == "pdf":
                pdf_ok = ok
            elif key == "photo":
                photo_ok = ok
            else:
                meeting_ok = ok
            if err is not None:
                errors[key] = err
    _probe = OptionalModulesProbe(pdf=pdf_ok, photo=photo_ok, meeting=meeting_ok, errors=errors)
    return _probe


def install_optional_modules_probe(probe: OptionalModulesProbe) -> None:
    """写入全局探测结果（例如渐进挂载完成后与 pdf_module_available 对齐）。"""
    global _probe
    _probe = probe


def get_optional_modules_probe() -> OptionalModulesProbe | None:
    return _probe


def pdf_module_available() -> bool:
    return bool(_probe and _probe.pdf)


def photo_module_available() -> bool:
    return bool(_probe and _probe.photo)


def meeting_module_available() -> bool:
    return bool(_probe and _probe.meeting)


def last_optional_module_error(key: str) -> BaseException | None:
    """key 为 pdf | photo | meeting；无记录时返回 None。"""
    if not _probe:
        return None
    return _probe.errors.get(key)
