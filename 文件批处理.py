import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip

def find_duplicates(directory, file_type):
    """
    查找并删除重复的文件。
    """
    file_hashes = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_type):
                file_path = os.path.join(root, file)
                file_hash = hash_file(file_path)
                if file_hash in file_hashes:
                    os.remove(file_path)
                    print(f"Deleted duplicate file: {file_path}")
                else:
                    file_hashes[file_hash] = file_path

def hash_file(file_path):
    """
    计算文件的哈希值。
    """
    hasher = cv2.img_hash.PHash_create()
    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    return hasher.compute(image).tostring()

def add_watermark_to_image(image_path, watermark_text, output_path):
    """
    为图片添加水印。
    """
    image = Image.open(image_path).convert("RGBA")
    txt = Image.new("RGBA", image.size, (255, 255, 255, 0))

    # 使用Pillow的ImageDraw模块
    draw = ImageDraw.Draw(txt)
    font = ImageFont.truetype("arial.ttf", 40)
    text_width, text_height = draw.textsize(watermark_text, font=font)

    # 在右下角添加水印
    position = (image.size[0] - text_width - 10, image.size[1] - text_height - 10)
    draw.text(position, watermark_text, fill=(255, 255, 255, 128), font=font)

    watermarked = Image.alpha_composite(image, txt)
    watermarked.save(output_path)
    print(f"Watermarked image saved to: {output_path}")

def add_watermark_to_video(video_path, watermark_text, output_path):
    """
    为视频添加水印。
    """
    video = VideoFileClip(video_path)
    txt_clip = (TextClip(watermark_text, fontsize=24, color='white')
                .set_position(('right', 'bottom'))
                .set_duration(video.duration))
    watermarked = CompositeVideoClip([video, txt_clip])
    watermarked.write_videofile(output_path, codec='libx264')
    print(f"Watermarked video saved to: {output_path}")

def find_files(directory, file_type):
    """
    查找特定类型的文件。
    """
    files_found = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_type):
                files_found.append(os.path.join(root, file))
    return files_found

def delete_files(directory, file_type):
    """
    删除特定类型的文件。
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_type):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

if __name__ == "__main__":
    directory = '修改'
    watermark_text = 'mine'

    # 去重
    find_duplicates(directory, ('.jpg', '.jpeg', '.png', '.mp4', '.avi'))

    # 为图片添加水印
    image_files = find_files(directory, ('.jpg', '.jpeg', '.png'))
    for image_file in image_files:
        add_watermark_to_image(image_file, watermark_text, image_file)

    # 为视频添加水印
    video_files = find_files(directory, ('.mp4', '.avi'))
    for video_file in video_files:
        add_watermark_to_video(video_file, watermark_text, video_file)

    # 删除特定类型的文件（例如删除所有 .tmp 文件）
    delete_files(directory, '.docx')