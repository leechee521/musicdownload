from typing import Any, Dict, Optional


class MyResponse:
    """
    通用响应类
    示例：
        success: Response.ok(data={"id": 1})
        error: Response.error(msg="参数错误", code=400)
    """

    def __init__(
            self,
            success: bool,
            code: int = 200,
            message: str = "",
            data: Optional[Any] = None,
    ):
        self.success = success
        self.code = code
        self.message = message
        self.data = data if data is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（适合JSON序列化）"""
        return {
            "success": self.success,
            "code": self.code,
            "message": self.message,
            "data": self.data,
        }

    def set_data(self, data: Any) -> 'MyResponse':
        """链式设置数据"""
        self.data = data
        return self

    def set_message(self, message: str) -> 'MyResponse':
        """链式设置消息"""
        self.message = message
        return self

    @classmethod
    def ok(
            cls,
            message: str = "操作成功",
            code: int = 200,
            data: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """成功响应"""
        return cls(True, code, message, data).to_dict()

    @classmethod
    def error(
            cls,
            message: str = "操作失败",
            code: int = 400,
            data: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """错误响应"""
        return cls(False, code, message, data).to_dict()

    @classmethod
    def from_exception(cls, e: Exception, code: int = 500) -> Dict[str, Any]:
        """从异常生成响应"""
        return cls.error(message=str(e), code=code)