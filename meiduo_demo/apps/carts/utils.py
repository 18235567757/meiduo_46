import base64
import pickle

from django_redis import get_redis_connection


def merge_cookie_to_redis(request, user, response):
    # 1.获取cookie数据
    cookie_str = request.COOKIES.get('carts')
    if cookie_str is not None:
        cookie_dict = pickle.loads(base64.b64decode(cookie_str))
    # 2.把redis数据读取下来
        redis_conn = get_redis_connection('carts')

        id_count_bytes = redis_conn.hgetall('carts_%s' % user.id)

        selected_ids = redis_conn.smembers('selected_%s' % user.id)

        id_count_redis = {}
        # redis读出的数据都是bytes类型
        for id, count in id_count_bytes.items():
            id_count_redis[int(id)] = int(count)

        # 初始化一个字典
        new_hash_update_data = {}
        # 一个列表用于记录选中的id
        selected_list = []
        # 一个列表用于记录未选中的id
        unselected_list = []
        # 3.对cookie数据进行遍历
        for sku_id,count_selected_dict in cookie_dict.items():
            if sku_id in id_count_redis:
                new_hash_update_data[sku_id] = count_selected_dict['count']
            else:
                new_hash_update_data[sku_id] = count_selected_dict['count']

            # 选中状态以ｃｏｏｋｉｅ为主
            if count_selected_dict['selected']:
                selected_list.append(sku_id)
            else:
                unselected_list.append(sku_id)
        # 4.将合并的数据更新到redis中
            redis_conn.hmset('carts_%s'% user.id, new_hash_update_data)

            if len(selected_list) > 0:
                redis_conn.sadd('selected_%s' % user.id, *selected_list)

            if len(unselected_list) > 0:
                redis_conn.srem('selected_%s' % user.id, *unselected_list)

        # 5.删除cookie数据

            response.delete_cookie('carts')

            return response

        else:
            return response
