from common.response import MyResponse
from typing import Any, Dict, Optional


class PaginatedResponse(MyResponse):
    """支持分页的响应"""

    def __init__(
            self,
            success: bool,
            code: int = 200,
            message: str = "",
            data: Optional[Any] = None,
            total: int = 0,
            page: int = 1,
    ):
        super().__init__(success, code, message, data)
        self.total = total
        self.page = page

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"total": self.total, "page": self.page})
        return base


# # 使用示例
# resp = PaginatedResponse.ok(
#     data=[...],
#     total=100,
#     page=2
# )
