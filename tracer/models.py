from django.db import models


# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(verbose_name='Username', max_length=100,unique=True, db_index=True)
    email = models.EmailField(verbose_name='Email',
                              unique=True, max_length=100, db_index=True)
    mobile_phone = models.CharField(
        verbose_name='MobilePhone', max_length=17, db_index=True)
    # mobile_phone = PhoneNumberField(null=False, blank=False, unique=True)
    password = models.CharField(verbose_name='Password', max_length=100)
    
    def __str__(self):
        return self.username
    
    
class PricePolicy(models.Model):
    category_choices = (
        (1, 'Free'),
        (2, 'Pay'),
        (3, 'Other')
    )
    category = models.SmallIntegerField(verbose_name='Pay Type', default=1, choices=category_choices)
    title = models.CharField(verbose_name='Title', max_length=32)
    price = models.PositiveIntegerField(verbose_name='Price')
    
    project_num = models.PositiveIntegerField(verbose_name='Project Number')
    project_member = models.PositiveIntegerField(verbose_name='Project Member')
    project_space = models.PositiveIntegerField(verbose_name='Single Project Space (GB)')
    per_file_size = models.PositiveIntegerField(verbose_name='Per File Size (MB)')
    
    create_datetime = models.DateTimeField(verbose_name='Create Datetime', auto_now_add=True)
    
    
class Transaction(models.Model):
    status_choices = (
        (1, 'Unpaid'),
        (2, 'Paid'),
    )
    
    status = models.SmallIntegerField(verbose_name='Status', choices=status_choices)
    
    order = models.CharField(verbose_name='Order Number', max_length=64, unique=True)
    user = models.ForeignKey(to='UserInfo', verbose_name='User', on_delete=models.CASCADE)
    price_policy = models.ForeignKey(to='PricePolicy', verbose_name='Price Policy', on_delete=models.CASCADE)
    
    count = models.IntegerField(verbose_name='Count (Year)', help_text='Zero means forever')
    
    price = models.IntegerField(verbose_name='Actually Paid Price')
    
    start_datetime = models.DateTimeField(verbose_name='Start Datetime', null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name='End Datetime', null=True, blank=True)
    
    create_datetime = models.DateTimeField(verbose_name='Create Datetime', auto_now_add=True)
    
    
class Project(models.Model):
    
    COLOR_CHOICES = (
        (1, '#56b8eb'),
        (2, '#f28033'),
        (3, '#ebc656'),
        (4, '#a2d148'),
        (5, '#20BFA4'),
        (6, '#7461c2'),
        (7, '#20bfa3'),
        (8, '#f6a739'),
        (9, '#F538A9'),
        (10, '#A5D6A7'),
        )
    
    name = models.CharField(verbose_name='Name', max_length=128)
    color = models.SmallIntegerField(verbose_name='Color', default=1, choices=COLOR_CHOICES)
    description= models.CharField(verbose_name='Description', max_length=255, null=True, blank=True)
    use_space = models.BigIntegerField(
        verbose_name='Used Space (Bytes)', default=0, help_text='Bytes')
    star = models.BooleanField(verbose_name='Star', default=False)
    
    bucket = models.CharField(verbose_name='COS Bucket Name', max_length=128) # tencent cos cloud storage bucket name
    region = models.CharField(verbose_name='COS Region', max_length=32) # tencent cos cloud storage region
    
    join_count = models.IntegerField(verbose_name='Join Member Count', default=1)
    creator = models.ForeignKey(to='UserInfo', verbose_name='Creator', on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='Create Datetime', auto_now_add=True)
    
    
class ProjectUser(models.Model):
    """Project member"""
    user = models.ForeignKey(to='UserInfo', verbose_name='User', on_delete=models.CASCADE, related_name='projects')
    project = models.ForeignKey(to='Project', verbose_name='Project', on_delete=models.CASCADE)
    
    # invitee = models.ForeignKey(to='UserInfo', verbose_name='Invitee', on_delete=models.CASCADE, null=True, blank=True,
    #                             related_name='invitees')
    
    star = models.BooleanField(verbose_name='Star', default=False)
    
    create_datetime = models.DateTimeField(verbose_name='Join Datetime', auto_now_add=True)
    
    
class Wiki(models.Model):
    project = models.ForeignKey(to='Project', verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=128)
    content = models.TextField(verbose_name='Content')
    # content = MDTextField(verbose_name='Content')
    # create_datetime = models.DateTimeField(verbose_name='Create Datetime', auto_now_add=True)
    
    depth = models.IntegerField(verbose_name='Depth', default=1)
    
    # 子关联
    parent = models.ForeignKey(to='self', verbose_name='Parent Article', 
                               on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    def __str__(self):
        return self.title
    
    
class File(models.Model):
    """File system"""
    file_type_choices = (
        (1, 'File'),
        (2, 'Folder'),
    )
    project = models.ForeignKey(to='Project', verbose_name='Project', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name', max_length=128, help_text='File/Folder name')
    file_type = models.SmallIntegerField(verbose_name='Type', choices=file_type_choices) # 1: file, 2: folder
    file_size = models.BigIntegerField(verbose_name='Size', null=True, blank=True, help_text='bytes')
    file_path = models.CharField(verbose_name='File Path', max_length=255, null=True, blank=True) # the location of the file on the tencent cos server
    parent = models.ForeignKey(to='self', verbose_name='Parent Folder', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    key = models.CharField(verbose_name='cos key', max_length=128, null=True, blank=True) # the name stored in cos
    update_user = models.ForeignKey(to='UserInfo', verbose_name='Update User', on_delete=models.CASCADE)
    update_datetime = models.DateTimeField(verbose_name='Update Datetime', auto_now=True)
  
  
class Issues(models.Model):
    """Issues"""
    project = models.ForeignKey(to='Project', verbose_name='Project', on_delete=models.CASCADE)
    issues_type = models.ForeignKey(to='IssuesType', verbose_name='Issues type', on_delete=models.CASCADE)
    module = models.ForeignKey(to='Module', verbose_name='Module', on_delete=models.CASCADE, null=True, blank=True)
    
    subject = models.CharField(verbose_name='Subject', max_length=128)
    desc = models.TextField(verbose_name='Description', null=True, blank=True)
    
    priority_choices = (
        ("danger", "high"),
        ("warning", "middle"),
        ("success", "low"),
    )  
    priority = models.CharField(verbose_name='Priority', max_length=16, choices=priority_choices, default='danger')
    
    # 新建，处理中，已解决，已忽略，待反馈，已关闭，重新打开
    status_choices = (
        (1, 'New'),
        (2, 'Processing'),
        (3, 'Solved'),
        (4, 'Ignored'),
        (5, 'Feedback'),
        (6, 'Closed'),
        (7, 'Reopened'),
    )
    status = models.SmallIntegerField(verbose_name='Status', choices=status_choices, default=1)
    
    assign = models.ForeignKey(to='UserInfo', verbose_name='Assign to', on_delete=models.CASCADE, related_name='task',null=True, blank=True)
    
    attention = models.ManyToManyField(to='UserInfo', verbose_name='Attention', related_name='observe', blank=True)
    
    start_date = models.DateField(verbose_name='Start Date', null=True, blank=True)
    end_date = models.DateField(verbose_name='End Date', null=True, blank=True)
    
    mode_choices = (
        (1, 'Public Mode'),
        (2, 'Private Mode'),
    )
    mode = models.SmallIntegerField(verbose_name='Mode', choices=mode_choices, default=1)
    
    parent = models.ForeignKey(to='self', verbose_name='Parent Issue', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    creator = models.ForeignKey(to='UserInfo', verbose_name='Creator', on_delete=models.CASCADE, related_name='create_problems')
    create_datetime = models.DateTimeField(verbose_name='Create Datetime', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='Latest Update Datetime', auto_now=True)
    
    def __str__(self):
        return self.subject
    
class Module(models.Model):
    """Module (Milestone) for issue tracking"""
    project = models.ForeignKey(to='Project', verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=128)

    
    def __str__(self):
        return self.title
    
    
class IssuesType(models.Model):
    """Issues type, such as Bug, Feature, Task, etc."""

    project = models.ForeignKey(to='Project', verbose_name='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=128)
    color = models.SmallIntegerField(verbose_name='Color')
    
    def __str__(self):
        return self.title