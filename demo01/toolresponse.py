from typing import Optional


class ToolResponse:
    """工具响应格式化类（支持直接调用）"""

    def __init__(self, tool_name: str, success: bool = True,
                 message: Optional[str] = None,
                 result_url: Optional[str] = None):
        """
        初始化工具响应

        Args:
            tool_name: 工具名称（必需）
            success: 是否执行成功
            message: 执行信息
            result_url: 结果链接
        """
        self.tool_name = tool_name
        self.success = success
        self.message = message
        self.result_url = result_url

    def __str__(self) -> str:
        """直接转换为格式化字符串"""
        return self._format_output()

    def _format_output(self) -> str:
        """格式化输出"""
        # 基础格式
        lines = [
            f"调用{self.tool_name}处理任务",
            f"执行结果：{'执行成功' if self.success else '执行失败'}"
        ]

        # 成功时的附加信息
        if self.success:
            if self.message:
                lines.append(f"执行信息：{self.message}")
            if self.result_url:
                lines.append(f"详情见链接：{self.result_url}")
        else:
            # 失败时的提示信息
            lines.append("请重试或者联系开发者")

        return "\n".join(lines)

    @classmethod
    def success(cls, tool_name: str, message: Optional[str] = None,
                result_url: Optional[str] = None) -> 'ToolResponse':
        """类方法：创建成功响应"""
        return cls(tool_name=tool_name, success=True, message=message, result_url=result_url)

    @classmethod
    def failure(cls, tool_name: str) -> 'ToolResponse':
        """类方法：创建失败响应"""
        return cls(tool_name=tool_name, success=False)


# 使用示例
if __name__ == "__main__":
    # 您现在可以这样直接调用！
    print("=== 直接调用方式 ===")

    # 成功用例 - 完整信息
    response1 = ToolResponse(
        tool_name="自动解决主机故障工具",
        success=True,
        message="故障解决步骤：\n1. 检查系统日志\n2. 重启服务\n3. 验证状态",
        result_url="https://monitor.example.com/host/123"
    )
    print(response1)

    print("\n" + "=" * 50 + "\n")

    # 成功用例 - 只有message
    response2 = ToolResponse(
        tool_name="数据备份工具",
        success=True,
        message="备份完成，文件大小：2.5GB"
    )
    print(response2)

    print("\n" + "=" * 50 + "\n")

    # 成功用例 - 只有result_url
    response3 = ToolResponse(
        tool_name="性能监控工具",
        success=True,
        result_url="https://dashboard.example.com/metrics"
    )
    print(response3)

    print("\n" + "=" * 50 + "\n")

    # 失败用例
    response4 = ToolResponse(
        tool_name="数据库迁移工具",
        success=False
    )
    print(response4)

    print("\n" + "=" * 50 + "\n")

    # 使用类方法（更简洁）
    print("=== 使用类方法 ===")

    # 成功响应
    success_response = ToolResponse.success(
        tool_name="自动部署工具",
        message="部署完成，版本v1.2.3",
        result_url="https://deploy.example.com/logs/456"
    )
    print(success_response)

    print("\n")

    # 失败响应
    failure_response = ToolResponse.failure("系统诊断工具")
    print(failure_response)