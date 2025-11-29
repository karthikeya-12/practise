""" import hashlib
from time import perf_counter

start = perf_counter()
with open("trying.py", "r") as file:
    data = file.read()
    hash = hashlib.sha256(data.encode("utf-8"))
    a = str(hash.hexdigest())
    print(len(a))
    print(a)
    end = perf_counter()
    print(f"Total time is {end - start:.6f}")

pp = {"hash_code": a}
print(f"Hello here is your hash code have a look {pp["hash_code"]}")
 """
from langchain_aws import ChatBedrock
from dotenv import load_dotenv
load_dotenv()
# llm = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0", region_name="us-east-1")
llm = ChatBedrock(model_id="qwen.qwen3-32b-v1:0", region_name="us-east-1")
print(llm.invoke("Hello"))
