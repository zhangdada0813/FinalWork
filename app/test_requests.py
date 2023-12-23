from concurrent.futures import ThreadPoolExecutor


para_dict = {"wow":1,'foo':2}
def simple_task(para_one,para_two):
    print(para_one,para_two)

print(list(para_dict.items()))
with ThreadPoolExecutor(max_workers=15) as exe:
    feature_to_item = [exe.submit(simple_task,goods_no,price) for goods_no,price in para_dict.items()]
    for result in feature_to_item:
        print(result.result()) 






