@cache(u'{0}.{1}x{2}.mp4')
def convert_mp4(filepath, width, height, opath):
    execute([
        'ffmpeg',
        '-i',
        filepath,
        '-vf',
        'scale={}:{}'.format(width, height),
        '-strict',
        '-2',
        '-movflags',
        '+faststart',
        opath
    ])

    return opath


def sample_clips(filepath, threshold=0.3, min_delta_time=1, accuracy=False):
    scenes = get_scene_info(filepath, threshold, min_delta_time)

    if accuracy:
        cut_function = cut_clip_accuracy
    else:
        cut_function = cut_clip

    def _iter():
        for scene in scenes:
            yield scene, cut_function(filepath, scene['from_ts'], scene['duration'])

    return list(_iter())


@cache("{0}-{1}.jpg")
def extract_frame(filepath, second, opath):
    execute([
        "ffmpeg",
        "-ss",
        second,
        "-i",
        filepath,
        "-vframes",
        1,
        opath
    ])
    return opath


@cache("{0}-blur.mp4")
def blur(filepath, mask_path, strength, opath):
    cmd = ['ffmpeg',
           '-i',
           str(filepath),
           '-i',
           str(mask_path),
           '-filter_complex',
           '[0:v][1:v]alphamerge,boxblur=10[alf];[0:v][alf]overlay[v]',
           '-map',
           '[v]',
           '-map',
           '0:a',
           '-c:v',
           'libx264',
           '-c:a',
           'copy',
           '-movflags',
           '+faststart',
           '-y',
           str(opath)]

    execute(cmd)

    return opath
