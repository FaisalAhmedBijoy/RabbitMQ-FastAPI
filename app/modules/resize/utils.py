"""Resize Utilities"""

from pathlib import Path


def create_output_directory():
    """Create output directory for resized images"""
    output_dir = Path("app/uploads/resized")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def validate_image(image_path: str) -> bool:
    """Validate image exists"""
    return Path(image_path).exists()
