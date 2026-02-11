from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import timedelta

@dataclass
class SongInfo:
    """
    歌曲信息类
    示例：
        from datetime import timedelta

    # 创建歌曲对象
    song = SongInfo(
        id="123456",
        title="海阔天空",
        artist="Beyond",
        album="乐与怒",
        duration=timedelta(minutes=5, seconds=24),
        source="qq",
        cover_url="https://example.com/cover.jpg"
    )

    print(song)
    """
    id: str  # 歌曲唯一标识
    title: str  # 歌曲名称
    artist: str  # 艺术家
    album: Optional[str] = None  # 专辑名称
    duration: Optional[timedelta] = None  # 时长
    source: Optional[str] = None  # 来源平台 (qq/wyy/kugou/kuwo)
    cover_url: Optional[str] = None  # 封面URL
    url: Optional[str] = None  # 播放URL
    lyric: Optional[str] = None  # 歌词

    # 附加元数据 (如音质、版权信息等)
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """初始化后处理"""
        self.metadata = self.metadata or {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SongInfo':
        """从字典创建对象"""
        return cls(
            id=str(data.get('id', '')),
            title=data.get('title', 'Untitled'),
            artist=data.get('artist', 'Unknown'),
            album=data.get('album'),
            duration=data.get('duration'),
            source=data.get('source'),
            cover_url=data.get('cover_url'),
            url=data.get('url'),
            lyric=data.get('lyric'),
            metadata=data.get('metadata', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（适合JSON序列化）"""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'source': self.source,
            'cover_url': self.cover_url,
            'url': self.url,
            'lyric': self.lyric,
            'metadata': self.metadata
        }

    def __str__(self) -> str:
        """友好显示"""
        return f"{self.title} - {self.artist} ({self.duration})"
