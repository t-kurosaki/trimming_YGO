from logging import getLogger, StreamHandler, DEBUG, INFO, Formatter, handlers

def set_logger(module_name,log_file_name):
    #ロガーを生成
    logger = getLogger(module_name)
    logger.handlers.clear()
    # 標準エラー出力のハンドラ生成
    streamHandler = StreamHandler()
    # 指定ファイルサイズによるログローテーション(maxBytes=0:無制限)
    fileHandler = handlers.RotatingFileHandler(
        log_file_name, maxBytes=0, backupCount=1)
    # フォーマッタの作成
    formatter = Formatter(
        "[%(asctime)s][%(name)s](%(levelname)s) %(message)s")
    streamHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)
    # エラーレベルを設定
    logger.setLevel(DEBUG)
    streamHandler.setLevel(INFO)
    fileHandler.setLevel(DEBUG)
    # ロガーにファイルハンドラを登録
    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)

    return logger

