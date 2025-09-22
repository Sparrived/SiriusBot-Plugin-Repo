from sirius_chat_core.models import FilterModel
from sirius_chat_core.models.model_platform import SiliconFlow

if __name__ == "__main__":
    platform = SiliconFlow("")

    # -------- 测试 FilterModel --------
    filter_model = FilterModel("Qwen/Qwen3-8B", platform=platform)
    response = filter_model._response(filter_model.create_initial_message_chain("小心我刀你，知不知道什么叫做黑手！"))
    print(response)