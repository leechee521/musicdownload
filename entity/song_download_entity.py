from dataclasses import dataclass


class SongDownloadEntity:

    def __init__(self, name, album, singer, pic, lyric, music_url, song_fomart, md5_value, size, publish_time,
                 no, singer_imga):
        super().__init__()
        self.name = name
        self.album = album
        self.singer = singer
        self.pic = pic
        self.lyric = lyric
        self.music_url = music_url
        self.song_fomart = song_fomart
        self.md5_value = md5_value
        self.size = size
        self.publish_time = publish_time
        self.no = no
        self.singer_img = singer_imga

    def singer_name1(self):
        singer_names = ""
        if len(self.singer) > 1:
            singer_names = ', '.join([s for s in self.singer])
        else:
            singer_names = self.singer[0]
        return singer_names

    def singer_name2(self):
        if len(self.singer) > 1:
            singer_names = ' / '.join([s for s in self.singer])
        else:
            singer_names = self.singer[0]
        return singer_names
