import os
import traceback

from app.config import Config
from app.log import Logger


def main():
    try:
        # 获取项目根目录
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # 配置文件路径
        config_file = os.path.join(base_dir, "config.yaml")

        # 加载配置
        config = Config(config_file)

        Logger().info("配置加载成功")

        # 测试读取配置
        print(config)

        #
        # TODO:
        # 在这里启动你的微信业务逻辑
        #
        # worker = WechatWorker(config)
        # worker.start()

    except Exception:
        Logger().fatal(traceback.format_exc())


if __name__ == "__main__":
    main()
