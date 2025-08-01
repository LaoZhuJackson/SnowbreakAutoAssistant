from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import threading

from cli.cli_task import CliTask


class RequestHandler(BaseHTTPRequestHandler):
    # 类级别的CliTask实例，确保单例
    _cli_task = None
    _task_running = False
    _task_thread = None

    def log_message(self, format, *args):
        """重写日志方法 - 禁用默认的访问日志"""
        # 完全禁用日志，注释掉下面这行
        pass

        # 或者自定义日志格式
        # print(f"[{self.log_date_time_string()}] {format % args}")

    # Handler for the GET requests
    def do_GET(self):

        # 解析URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        # 根据路由执行不同操作
        if path == '/' or path == '/home':
            self.handle_home()
        elif path == '/api/start':
            self.handle_start()
        elif path == '/api/stop':
            self.handle_stop()
        elif path == '/api/status':
            self.handle_status()
        else:
            self.handle_404()

    def send_json_response(self, status_code, response_data):
        """通用的JSON响应方法"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

    def handle_home(self):
        """处理首页请求"""
        response = {"message": "Welcome to SnowbreakAutoAssistant", "version": "2.0.6"}
        self.send_json_response(200, response)

    def _run_task_in_background(self):
        """在后台线程中运行任务"""
        try:
            print("开始执行后台任务...")
            RequestHandler._cli_task.run()
            print("后台任务执行完成")
        except Exception as e:
            print(f"后台任务执行失败: {str(e)}")
        finally:
            # 任务完成或失败，重置运行状态
            RequestHandler._task_running = False
            RequestHandler._task_thread = None

    def handle_start(self):
        """处理启动请求"""
        try:
            # 检查是否已有任务在运行
            if RequestHandler._task_running:
                response = {"action": "start", "result": "warning", "message": "Task is already running"}
                self.send_json_response(200, response)
                return

            # 如果没有CliTask实例，创建一个
            if RequestHandler._cli_task is None:
                RequestHandler._cli_task = CliTask()

            # 标记任务正在运行
            RequestHandler._task_running = True

            # 在后台线程中运行任务
            RequestHandler._task_thread = threading.Thread(
                target=self._run_task_in_background,
                daemon=True  # 设置为守护线程，主程序退出时自动结束
            )
            RequestHandler._task_thread.start()

            response = {"action": "start", "result": "success", "message": "Assistant task started in background"}
        except Exception as e:
            # 发生异常时重置运行状态
            RequestHandler._task_running = False
            RequestHandler._task_thread = None
            response = {"action": "start", "result": "error", "message": f"Failed to start assistant: {str(e)}"}
        self.send_json_response(200, response)

    def handle_stop(self):
        """处理停止请求"""
        if RequestHandler._task_running:
            RequestHandler._task_running = False
            # 注意：这里只是设置标志位，实际的任务停止需要在CliTask中实现
            response = {"action": "stop", "result": "success", "message": "Stop signal sent to running task"}
        else:
            response = {"action": "stop", "result": "info", "message": "No task is currently running"}
        self.send_json_response(200, response)

    def handle_status(self):
        """处理状态查询请求"""
        thread_alive = RequestHandler._task_thread is not None and RequestHandler._task_thread.is_alive()
        response = {
            "action": "status",
            "result": "success",
            "data": {
                "task_running": RequestHandler._task_running,
                "thread_alive": thread_alive,
                "has_cli_task": RequestHandler._cli_task is not None
            }
        }
        self.send_json_response(200, response)

    def handle_404(self):
        """处理404错误"""
        response = {"error": "Not Found", "message": "The requested resource was not found"}
        self.send_json_response(404, response)

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"SAA cli running on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
