# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings
from sts.sts import Sts

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
    
    # add cors rule
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD'],
                'AllowedHeader': '*',
                'ExposeHeader': '*',
                'MaxAgeSeconds': 500
            }
        ]
    }
    
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )


def upload_buffer_file(bucket: str, file_object, key, region: str = 'ap-shanghai'):
    """upload image to tencent cos"""
    
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


def delete_file(bucket: str, key, region: str = 'ap-shanghai'):
    """delete a single file on tencent cos"""

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    client.delete_object(
        Bucket=bucket,
        Key=key,
    )

        
def delete_file_list(bucket: str, key_list: list, region: str = 'ap-shanghai'):
    """批量删除cos文件"""
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    
    objects = {
        "Quiet": "true",
        "Object": key_list
    }
    
    client.delete_objects(
        Bucket = bucket,
        Delete = objects
    )
    

def create_crendentials(bucket: str, region: str = 'ap-shanghai'):
    """
    获取cos的credentials
    https://github.com/tencentyun/qcloud-cos-sts-sdk/blob/2efeb10ca2f63d2100d445ea4c87f35bb475b19a/python/demo/sts_demo.py#L6
    """
    
    config = {
        'url': 'https://sts.tencentcloudapi.com/',
        # 域名，非必须，默认为 sts.tencentcloudapi.com
        'domain': 'sts.tencentcloudapi.com',
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        'secret_id': secret_id,
        # 固定密钥
        'secret_key': secret_key,
        # 设置网络代理
        # 'proxy': {
        #     'http': 'xx',
        #     'https': 'xx'
        # },
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 简单上传
            'name/cos:PutObject',
            'name/cos:PostObject',
            # 分片上传
            'name/cos:InitiateMultipartUpload',
            'name/cos:ListMultipartUploads',
            'name/cos:ListParts',
            'name/cos:UploadPart',
            'name/cos:CompleteMultipartUpload'
        ],

    }
    
    sts = Sts(config)
    response = sts.get_credential()

    return response