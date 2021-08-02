import concurrent.futures
import threading

app_thread_pool_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
event = threading.Event()