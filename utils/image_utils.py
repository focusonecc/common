# -*- coding: utf-8 -*-
# @Author: theo-l
# @Date:   2017-07-05 12:49:02
# @Last Modified by:   theo-l
# @Last Modified time: 2017-07-08 20:57:49
from PIL import Image
from six import StringIO

from django.core.files.uploadedfile import InMemoryUploadedFile


def gen_watermark_and_thumbnail_of_image(source, watermark_path=None, thumbnail_width=640):
    """
    :source: an instance of django's InMemoryUploadedFile
    """
    # TODO: need to specify the real watermark_path
    with Image.open(source) as source_img, Image.open(watermark_path) as watermark_source_img:
        file_ext = source.name.split('.')[-1].lower()
        mimetype = 'image/{}'.format(file_ext)

        source_img = Image.open(source)

        # use the copy version
        watermark_img = watermark_source_img.copy()

        ratio = 0.55
        wm_ratio = watermark_img.size[1] / float(watermark_img.size[0])

        wm_width = int(source_img.size[0] * ratio)
        wm_height = int(wm_ratio * wm_width)

        wm_left = int((source_img.size[0] - wm_width) / 2.0)
        wm_top = int((source_img.size[1] - wm_height) / 2.0)
        wm_right = wm_left + wm_width
        wm_bottom = wm_top + wm_height

        box = (wm_left, wm_top, wm_right, wm_bottom)
        watermark_img.thumbnail((wm_width, wm_height))

        # paste the watermark photo to the original one
        source_img.paste(watermark_img, box, watermark_img)

        # source_img.show()
        source_img_io = StringIO.StringIO()
        source_img.save(source_img_io, file_ext)
        watermarked_file = InMemoryUploadedFile(source_img_io, None, source.name, mimetype, source_img_io.len, None)

        # gen thumbnail
        t_width = thumbnail_width
        source_ratio = source_img.size[1] / float(source_img.size[0])
        t_height = int(t_width * source_ratio)
        thumbnail = source_img.resize((t_width, t_height))
        # thumbnail.show()
        thumbnail_io = StringIO.StringIO()
        thumbnail.save(thumbnail_io, file_ext)
        thumbnail_file = InMemoryUploadedFile(thumbnail_io, None, source.name, mimetype, thumbnail_io.len, None)
        return watermarked_file, thumbnail_file
