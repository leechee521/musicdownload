from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SongTopList:
    id: str
    title: str  # 标题
    source: Optional[str] = None  # 来源平台 (qq/wyy/kugou/kuwo)

    # 附加元数据 (如音质、版权信息等)
    songs: Dict[str, Any] = None

    def __post_init__(self):
        """初始化后处理"""
        self.songs = self.songs or {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SongTopList':
        """从字典创建对象"""
        return cls(
            id=data['id'],
            title=data.get('title', 'Untitled'),
            source=data.get('source'),
            songs=data.get('songs', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（适合JSON序列化）"""
        return {
            'id': self.id,
            'title': self.title,
            'source': self.source,
            'songs': self.songs
        }
