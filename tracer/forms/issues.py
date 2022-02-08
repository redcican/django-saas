from django import forms
from tracer import models
from tracer.forms.bootstrap import BootstrapForm
from tracer.models import Issues
from bootstrap_datepicker_plus.widgets import DatePickerInput



class IssuesModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        
        widgets = {
            "assign": forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            #"issues_type": forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            "module": forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            "parent": forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            "attention": forms.SelectMultiple(attrs={'class': "selectpicker", 'data-live-search': "true",
                                                     "data-actions-box":"true"}),
            'start_date': DatePickerInput(),  # default date-format %m/%d/%Y will be used
            # specify date-frmat
            'end_date': DatePickerInput(),
        }
        
    def __init__(self,request, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        
        # 初始化时，设置默认值
        # 1. 获取当前项目的所有问题类型
        # issues_type_list = [("", "Nothing selected")]
        issues_type_list = models.IssuesType.objects.filter(project=request.tracer.project).values_list('id','title')
        
        self.fields['issues_type'].choices = issues_type_list
        
        # 2. 获取当前项目的所有模块
        module_list = [("", "Nothing selected")]
        moduel_object_list = models.Module.objects.filter(project=request.tracer.project).values_list('id', 'title')
        module_list.extend(moduel_object_list)
        self.fields['module'].choices = module_list
        
        # 3. 指派给谁 和 关注者
        # 找到当前项目的参与者和创建者
        total_user_list = [(request.tracer.project.creator_id, request.tracer.project.creator.username), ]
        project_user_list = models.ProjectUser.objects.filter(project=request.tracer.project).values_list('user_id','user__username')
        
        total_user_list.extend(project_user_list)
        
        self.fields['assign'].choices = [("", "Nothing selected")] + total_user_list
        self.fields['attention'].choices = total_user_list
        
        
        # 4。 获取当前项目的所有父级问题
        parent_list = [("", "Nothing selected")]
        parent_object_list = models.Issues.objects.filter(project=request.tracer.project).values_list('id', 'subject')
        parent_list.extend(parent_object_list)
        self.fields['parent'].choices =  parent_list
        
        
class IssuesReplyModelForm(forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']