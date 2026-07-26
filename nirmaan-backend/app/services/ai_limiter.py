import time

LAST_CALL = 0
DELAY = 3

def wait_if_needed():
    global LAST_CALL

    now = time.time()

    if now - LAST_CALL < DELAY:
        time.sleep(DELAY)

    LAST_CALL = time.time()