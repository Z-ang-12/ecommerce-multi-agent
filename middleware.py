import time

async def add_request_logging(request, call_next):
    """中间件：记录每个请求的方法、路径和耗时"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"⏱️ {request.method} {request.url.path} - 耗时: {process_time:.3f}秒")
    return response