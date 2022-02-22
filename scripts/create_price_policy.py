
import base
from tracer import models



def run():
    # offline script to create price policy for paid users
    models.PricePolicy.objects.create(
            category=2,
            title="VIP",
            price=100,
            project_num=50,
            project_member=10,
            project_space=10,
            per_file_size=500,
        )
    models.PricePolicy.objects.create(
            category=2,
            title="SVIP",
            price=200,
            project_num=150,
            project_member=110,
            project_space=110,
            per_file_size=1024,
        )
    models.PricePolicy.objects.create(
            category=2,
            title="SSVIP",
            price=500,
            project_num=550,
            project_member=510,
            project_space=510,
            per_file_size=2048,
        )


if __name__ == '__main__':
    run()
