import requests
import redis
import schedule
import time


# 连接数据库
reids_pool = redis.Redis(host='127.0.0.1', port=6379)


def proxy():
    def start():
        counts = reids_pool.hgetall('proxies')
        if len(counts) < 4:
            proxies = requests.get('http://svip.kdlapi.com/api/getproxy/?orderid=938132027465769&num=5&protocol=1&method=2&an_ha=1&sp1=1&sp2=1&quality=2&sort=1&dedup=1&sep=1').text.split()
            for proxy in proxies:
                # 保存到 Redis 数据库
                if ':' in proxy:
                    reids_pool.hset('proxies', proxy, proxy)
                    print(time.time(), proxy)

    start()
    # 每 1s 刷新一次代理
    schedule.every(1).seconds.do(start)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    proxy()
    # a = reids_pool.keys('200.89.178.182:80')
