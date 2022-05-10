import concurrent.futures
import threading
import queue

app_thread_pool_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
event = threading.Event()
pipeline = queue.Queue(maxsize=10)