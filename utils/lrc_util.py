def parse_lyrics(lyrics):
    lines = lyrics.split('\n')
    parsed = {}
    for line in lines:
        if line.startswith('[') and ']' in line:
            time_part = line.split(']')[0][1:]
            text = line.split(']', 1)[1].strip()
            # 只处理标准时间戳（如 00:08.000），忽略其他元数据（如 by:... 或 作词 : ...）
            if ':' in time_part and '.' in time_part and len(time_part.split(':')) == 2:
                parsed[time_part] = text
    return parsed


def merge_lyrics(s1, s2):
    chinese = parse_lyrics(s1)
    english = parse_lyrics(s2)

    # 获取所有时间点并排序
    all_times = sorted(set(chinese.keys()).union(set(english.keys())))

    merged = []
    for time in all_times:
        cn_line = chinese.get(time, None)
        en_line = english.get(time, None)

        if cn_line is not None:
            merged.append(f"[{time}]{cn_line}")
        if en_line is not None:
            merged.append(f"[{time}]{en_line}")

    return '\n'.join(merged)