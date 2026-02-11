import os.path


class SimpleM3UGenerator:

    def __init__(self, ):
        """
        初始化歌单生成器

        :param playlist_title: 歌单标题(会显示在#PLAYLIST行)
        """
        self.playlist_title = None
        self.playlist_id = None
        self._entries = []

    def add_song(self, artist: str, title: str, path: str) -> None:
        """
        添加一首歌曲到歌单

        :param artist: 歌手名
        :param title: 歌曲名
        :param path: 歌曲文件路径
        """
        self._entries.append({
            'artist': artist,
            'title': title,
            'path': path
        })

    def save(self, path: str) -> None:
        """
        保存歌单到文件

        :param output_path: 输出文件路径
        """
        output_path = os.path.join(".", "downloads", "playlist", path)
        os.makedirs(output_path, exist_ok=True)
        output_path = os.path.join(output_path, str(self.playlist_id) + ".m3u")
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入文件头
            f.write("#EXTM3U\n")
            f.write(f"#PLAYLIST:{self.playlist_title}\n")

            # 写入每首歌曲
            for song in self._entries:
                f.write(f"#EXTINF:{song['artist']} - {song['title']}\n")
                f.write(f"{song['path']}\n")

    def __str__(self) -> str:
        """返回当前歌单内容字符串"""
        lines = [
            "#EXTM3U",
            f"#PLAYLIST:{self.playlist_title}"
        ]

        for song in self._entries:
            lines.append(f"#EXTINF:{song['artist']} - {song['title']}")
            lines.append(song['path'])

        return "\n".join(lines)

    @property
    def song_count(self) -> int:
        """返回歌单中的歌曲数量"""
        return len(self._entries)
