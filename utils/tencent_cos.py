# -*- coding=utf-8
from django.test import client
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings

# 正常情况日志级别使用INFO，需要定位时可以修改为DEBUG，此时SDK会打印和服务端的通信信息
# logging.basicConfig(level=logging.INFO, stream=sys.stdout)

secret_id = settings.TENCENT_COS_SECRET_ID
secret_key = settings.TENCENT_COS_SECRET_KEY

def create_bucket(bucket: str, region: str='ap-shanghai'):
    # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
    # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
    # secret_id = secret_id
    # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
    # secret_key = secret_key
    # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
    # region = 'ap-beijing'
    # COS支持的所有region列表参见https://cloud.tencent.com/document/product/436/6224
    # 如果使用永久密钥不需要填入token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见https://cloud.tencent.com/document/product/436/14048
    token = None
    scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

    config = CosConfig(Region=region, SecretId=secret_id,
                    SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    
    client.create_bucket(
        Bucket=bucket,
        ACL='public-read',
    )


def upload_buffer_file(bucket: str, file_object, key, region: str = 'ap-shanghai'):
    
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    
    client.upload_file_from_buffer(
        Bucket=bucket,
        Body = file_object,
        Key= key,
    )
    
    image_url = client.get_object_url(
        Bucket=bucket,
        Key=key
    )
    
    return image_url
    
    
    