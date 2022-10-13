import uuid
def random_string(length):
  if length > 32:
    length = 32
  hex = uuid.uuid4().hex[:length]	
  return hex