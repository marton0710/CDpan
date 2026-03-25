import os
import uuid

from pypdf import PdfReader, PdfWriter

TRACKING_METADATA_KEY = "/CDPanTrackingId"


def read_pdf_tracking_id(file_path: str) -> str | None:
    """
    读取 PDF 追踪 id
    :param file_path:文件路径
    :return:追踪 id
    """
    reader = PdfReader(file_path)
    metadata = reader.metadata or {}
    tracking_id = metadata.get(TRACKING_METADATA_KEY)
    if not tracking_id:
        return None
    return str(tracking_id)


def write_pdf_tracking_id(file_path: str, tracking_id: str) -> bool:
    """
    将指定追踪 id 写入 PDF
    :param file_path:文件路径
    :param tracking_id:目标追踪 id
    :return:是否写入过元数据
    """
    current_tracking_id = read_pdf_tracking_id(file_path)
    if current_tracking_id == tracking_id:
        return False

    reader = PdfReader(file_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    metadata = {}
    if reader.metadata:
        for key, value in reader.metadata.items():
            if key is not None and value is not None:
                metadata[str(key)] = str(value)
    metadata[TRACKING_METADATA_KEY] = tracking_id
    writer.add_metadata(metadata)

    temp_path = f"{file_path}.tmp"
    with open(temp_path, "wb") as f:
        writer.write(f)
    os.replace(temp_path, file_path)
    return True


def ensure_pdf_tracking_id(file_path: str) -> tuple[str, bool]:
    """
    确保 PDF 带有追踪 id
    :param file_path:文件路径
    :return:追踪 id 和是否写入过元数据
    """
    tracking_id = read_pdf_tracking_id(file_path)
    if tracking_id:
        return tracking_id, False

    tracking_id = str(uuid.uuid4())
    return tracking_id, write_pdf_tracking_id(file_path, tracking_id)
