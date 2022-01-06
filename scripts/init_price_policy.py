
import base
from tracer import models

def run():
    exists = models.PricePolicy.objects.filter(category=1, title='Personal Free').exists()
    if not exists:
        models.PricePolicy.objects.create(
        category = 1,
        title = "Personal Free",
        price = 0,
        project_num = 3,
        project_member = 2,
        project_space = 20,
        per_file_size = 5
    )
        
if __name__ == '__main__':
    run()