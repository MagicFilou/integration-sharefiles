import redis
import json

from settings import C
from utils.transform import columns_dict_w_include_list

from datetime import datetime

redis_client = redis.StrictRedis(C["Redis"]["Host"], C["Redis"]["Port"], C["Redis"]["Database"])


def save_structure_redis(structure):
  """Save structure message to redis"""

  print("save to redis", C["StructureOutputKey"])

  dump = json.dumps(structure)
  # Redis rpush
  redis_client.rpush(C["StructureOutputKey"], dump)

def save_packages_redis(packages):
  """Save package messages to redis"""

  print("save to redis", C["ContentOutputKey"])

  for pkg in packages:
    dump = json.dumps(pkg)
    # Redis rpush
    redis_client.rpush(C["ContentOutputKey"], dump)

def save_package_redis(package):
  """Save package message to redis"""

  # print("save to redis", C["ContentOutputKey"])

  print(package)
  dump = json.dumps(package)
  # Redis rpush
  redis_client.rpush(C["ContentOutputKey"], dump)