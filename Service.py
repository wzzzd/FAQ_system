# -*- encoding: UTF-8 -*-
# @Describe : 
# @Time : 
# @Author : 




import logging
import json
import time
import tornado.web
import tornado.gen
import tornado.ioloop
import tornado.options
import tornado.httpserver
from tornado.escape import json_decode
from tornado.options import define, options

from FAQ import FAQ
from utils.Logger import init_logger
from utils.DateOption import get_date
from utils.FileOp import File
from Config import Config



class FAQHandler(tornado.web.RequestHandler):
    """
    服务类
    """

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')


    @tornado.gen.coroutine
    def post(self):
        """
        处理POST请求
        :return:
        """
        logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Service start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        s_time = time.time()
        
        # 获取请求参数
        body = json_decode(self.request.body)
        ## 判断参数是否缺失
        if 'question' not in body:
            response = {
                'status': 400,
                'msg': 'Error: miss parameter "question".'
            }
            self.write(json.dumps(response, ensure_ascii=False))
            self.finish()
        query = body.get('question', '')
        size = body.get('size', 3)
        logger.info(">> query args: {}".format(body))

        # 主函数
        answer = faq.query(query, size=size)

        # 构造返回参数
        response = {
            'status': 200,
            'answer': answer
        }

        # 服务返回
        self.write(json.dumps(response, ensure_ascii=False))
        self.finish()

        # 记录日志
        cost_time = time.time()-s_time
        logger.info(">> response args: {}".format(response))
        logger.info(">> response time: {} sec".format(str(cost_time)))
        logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Service end >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")




if __name__ == "__main__":

    # 日志配置
    logger = init_logger('API Server')
    # 接口配置
    define("port", default=5000, help="run on the given port", type=int)  #接口配置
    config = Config()
    # 加载问答系统类
    faq = FAQ()
    # tornado配置 & 启动
    tornado.options.parse_command_line()
    # 根据配置文件，选择版本开关
    app = tornado.web.Application(handlers=[
            (r"/api/v1/faq/", FAQHandler),
        ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



