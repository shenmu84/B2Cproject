from django.db import models


class UmsAdmin(models.Model):
    """
    后台用户表
    """
    username = models.CharField(max_length=64, null=True, blank=True)
    password = models.CharField(max_length=64, null=True, blank=True)
    icon = models.CharField(max_length=500, null=True, blank=True, verbose_name='头像')
    email = models.CharField(max_length=100, null=True, blank=True, verbose_name='邮箱')
    nick_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='昵称')
    note = models.CharField(max_length=500, null=True, blank=True, verbose_name='备注信息')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    login_time = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')
    status = models.IntegerField(default=1, verbose_name='帐号启用状态：0->禁用；1->启用')

    def __str__(self):
        return self.username or "管理员"

    class Meta:
        db_table = 'ums_admin'
        verbose_name = '后台用户'
        verbose_name_plural = '后台用户'


class UmsAdminLoginLog(models.Model):
    """
    后台用户登录日志表
    """
    admin = models.ForeignKey(UmsAdmin, on_delete=models.SET_NULL, null=True, db_column='admin_id')
    create_time = models.DateTimeField(null=True, blank=True)
    ip = models.CharField(max_length=64, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    user_agent = models.CharField(max_length=100, null=True, blank=True, verbose_name='浏览器登录类型')

    def __str__(self):
        return f"{self.admin} 登录于 {self.create_time}"

    class Meta:
        db_table = 'ums_admin_login_log'
        verbose_name = '后台用户登录日志'
        verbose_name_plural = '后台用户登录日志'
from django.db import models


class UmsAdminPermissionRelation(models.Model):
    """
    后台用户和权限关系表（除角色中定义的权限以外的加减权限）
    """
    admin_id = models.BigIntegerField(null=True, blank=True)
    permission_id = models.BigIntegerField(null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ums_admin_permission_relation'
        verbose_name = '用户权限关系'
        verbose_name_plural = '用户权限关系'


class UmsAdminRoleRelation(models.Model):
    """
    后台用户和角色关系表
    """
    admin_id = models.BigIntegerField(null=True, blank=True)
    role_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ums_admin_role_relation'
        verbose_name = '用户角色关系'
        verbose_name_plural = '用户角色关系'


class UmsGrowthChangeHistory(models.Model):
    """
    成长值变化历史记录表
    """
    member_id = models.BigIntegerField(null=True, blank=True)
    create_time = models.DateTimeField(null=True, blank=True)
    change_type = models.IntegerField(null=True, blank=True, verbose_name='改变类型：0->增加；1->减少')
    change_count = models.IntegerField(null=True, blank=True, verbose_name='积分改变数量')
    operate_man = models.CharField(max_length=100, null=True, blank=True, verbose_name='操作人员')
    operate_note = models.CharField(max_length=200, null=True, blank=True, verbose_name='操作备注')
    source_type = models.IntegerField(null=True, blank=True, verbose_name='积分来源：0->购物；1->管理员修改')

    class Meta:
        db_table = 'ums_growth_change_history'
        verbose_name = '成长值变化记录'
        verbose_name_plural = '成长值变化记录'
class UmsIntegrationChangeHistory(models.Model):
    """
    积分变化历史记录表
    """
    member_id = models.BigIntegerField(null=True, blank=True)
    create_time = models.DateTimeField(null=True, blank=True)
    change_type = models.IntegerField(null=True, blank=True, verbose_name='改变类型：0->增加；1->减少')
    change_count = models.IntegerField(null=True, blank=True, verbose_name='积分改变数量')
    operate_man = models.CharField(max_length=100, null=True, blank=True, verbose_name='操作人员')
    operate_note = models.CharField(max_length=200, null=True, blank=True, verbose_name='操作备注')
    source_type = models.IntegerField(null=True, blank=True, verbose_name='积分来源：0->购物；1->管理员修改')

    class Meta:
        db_table = 'ums_integration_change_history'
        verbose_name = '积分变化记录'
        verbose_name_plural = '积分变化记录'


class UmsIntegrationConsumeSetting(models.Model):
    """
    积分消费设置表
    """
    deduction_per_amount = models.IntegerField(null=True, blank=True, verbose_name='每一元抵扣所需积分')
    max_percent_per_order = models.IntegerField(null=True, blank=True, verbose_name='每笔订单最高抵扣百分比')
    use_unit = models.IntegerField(null=True, blank=True, verbose_name='每次使用积分最小单位')
    coupon_status = models.IntegerField(null=True, blank=True, verbose_name='是否可与优惠券共用；0->否；1->是')

    class Meta:
        db_table = 'ums_integration_consume_setting'
        verbose_name = '积分消费设置'
        verbose_name_plural = '积分消费设置'
class UmsMember(models.Model):
    """
    会员表
    """
    member_level_id = models.BigIntegerField(null=True, blank=True)
    username = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name='用户名')
    password = models.CharField(max_length=64, null=True, blank=True, verbose_name='密码')
    nickname = models.CharField(max_length=64, null=True, blank=True, verbose_name='昵称')
    phone = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name='手机号码')
    status = models.IntegerField(null=True, blank=True, verbose_name='帐号启用状态:0->禁用；1->启用')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='注册时间')
    icon = models.CharField(max_length=500, null=True, blank=True, verbose_name='头像')
    gender = models.IntegerField(null=True, blank=True, verbose_name='性别：0->未知；1->男；2->女')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    city = models.CharField(max_length=64, null=True, blank=True, verbose_name='所在城市')
    job = models.CharField(max_length=100, null=True, blank=True, verbose_name='职业')
    personalized_signature = models.CharField(max_length=200, null=True, blank=True, verbose_name='个性签名')
    source_type = models.IntegerField(null=True, blank=True, verbose_name='用户来源')
    integration = models.IntegerField(null=True, blank=True, verbose_name='积分')
    growth = models.IntegerField(null=True, blank=True, verbose_name='成长值')
    luckey_count = models.IntegerField(null=True, blank=True, verbose_name='剩余抽奖次数')
    history_integration = models.IntegerField(null=True, blank=True, verbose_name='历史积分数量')

    class Meta:
        db_table = 'ums_member'
        verbose_name = '会员'
        verbose_name_plural = '会员'
class UmsMemberLoginLog(models.Model):
    member = models.BigIntegerField(null=True, blank=True)
    create_time = models.DateTimeField(null=True, blank=True)
    ip = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    login_type = models.IntegerField(null=True, blank=True, verbose_name='登录类型：0->PC；1->android;2->ios;3->小程序')
    province = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'ums_member_login_log'
        verbose_name = '会员登录记录'
        verbose_name_plural = '会员登录记录'
class UmsMemberMemberTagRelation(models.Model):
    member = models.BigIntegerField(null=True, blank=True)
    tag_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ums_member_member_tag_relation'
        verbose_name = '用户标签关系'
        verbose_name_plural = '用户标签关系'
class UmsMemberProductCategoryRelation(models.Model):
    member = models.BigIntegerField(null=True, blank=True)
    product_category_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ums_member_product_category_relation'
        verbose_name = '会员与产品分类关系'
        verbose_name_plural = '会员与产品分类关系'
class UmsMemberReceiveAddress(models.Model):
    member = models.BigIntegerField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='收货人名称')
    phone_number = models.CharField(max_length=64, null=True, blank=True)
    default_status = models.IntegerField(null=True, blank=True, verbose_name='是否为默认')
    post_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='邮政编码')
    province = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    detail_address = models.CharField(max_length=128, null=True, blank=True, verbose_name='详细地址')

    class Meta:
        db_table = 'ums_member_receive_address'
        verbose_name = '会员收货地址'
        verbose_name_plural = '会员收货地址'
from django.db import models

class UmsMemberRuleSetting(models.Model):
    continue_sign_day = models.IntegerField(null=True, blank=True, verbose_name='连续签到天数')
    continue_sign_point = models.IntegerField(null=True, blank=True, verbose_name='连续签到赠送数量')
    consume_per_point = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='每消费多少元获取1个点')
    low_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='最低获取点数的订单金额')
    max_point_per_order = models.IntegerField(null=True, blank=True, verbose_name='每笔订单最高获取点数')
    type = models.IntegerField(null=True, blank=True, verbose_name='类型：0->积分规则；1->成长值规则')

    class Meta:
        db_table = 'ums_member_rule_setting'
        verbose_name = '会员积分成长规则'
        verbose_name_plural = verbose_name


class UmsMemberStatisticsInfo(models.Model):
    member_id = models.BigIntegerField(null=True, blank=True)
    consume_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='累计消费金额')
    order_count = models.IntegerField(null=True, blank=True, verbose_name='订单数量')
    coupon_count = models.IntegerField(null=True, blank=True, verbose_name='优惠券数量')
    comment_count = models.IntegerField(null=True, blank=True, verbose_name='评价数')
    return_order_count = models.IntegerField(null=True, blank=True, verbose_name='退货数量')
    login_count = models.IntegerField(null=True, blank=True, verbose_name='登录次数')
    attend_count = models.IntegerField(null=True, blank=True, verbose_name='关注数量')
    fans_count = models.IntegerField(null=True, blank=True, verbose_name='粉丝数量')
    collect_product_count = models.IntegerField(null=True, blank=True)
    collect_subject_count = models.IntegerField(null=True, blank=True)
    collect_topic_count = models.IntegerField(null=True, blank=True)
    collect_comment_count = models.IntegerField(null=True, blank=True)
    invite_friend_count = models.IntegerField(null=True, blank=True)
    recent_order_time = models.DateTimeField(null=True, blank=True, verbose_name='最后一次下订单时间')

    class Meta:
        db_table = 'ums_member_statistics_info'
        verbose_name = '会员统计信息'
        verbose_name_plural = verbose_name


class UmsMemberTag(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    finish_order_count = models.IntegerField(null=True, blank=True, verbose_name='自动打标签完成订单数量')
    finish_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='自动打标签完成订单金额')

    class Meta:
        db_table = 'ums_member_tag'
        verbose_name = '用户标签'
        verbose_name_plural = verbose_name


class UmsMemberTask(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    growth = models.IntegerField(null=True, blank=True, verbose_name='赠送成长值')
    intergration = models.IntegerField(null=True, blank=True, verbose_name='赠送积分')
    type = models.IntegerField(null=True, blank=True, verbose_name='任务类型：0->新手任务；1->日常任务')

    class Meta:
        db_table = 'ums_member_task'
        verbose_name = '会员任务'
        verbose_name_plural = verbose_name
from django.db import models


class UmsPermission(models.Model):
    pid = models.BigIntegerField(null=True, blank=True, verbose_name='父级权限id')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='名称')
    value = models.CharField(max_length=200, null=True, blank=True, verbose_name='权限值')
    icon = models.CharField(max_length=500, null=True, blank=True, verbose_name='图标')
    type = models.IntegerField(null=True, blank=True, verbose_name='权限类型：0->目录；1->菜单；2->按钮（接口绑定权限）')
    uri = models.CharField(max_length=200, null=True, blank=True, verbose_name='前端资源路径')
    status = models.IntegerField(null=True, blank=True, verbose_name='启用状态；0->禁用；1->启用')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    sort = models.IntegerField(null=True, blank=True, verbose_name='排序')

    class Meta:
        db_table = 'ums_permission'
        verbose_name = '后台用户权限'
        verbose_name_plural = verbose_name


class UmsResource(models.Model):
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    name = models.CharField(max_length=200, null=True, blank=True, verbose_name='资源名称')
    url = models.CharField(max_length=200, null=True, blank=True, verbose_name='资源URL')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='描述')
    category_id = models.BigIntegerField(null=True, blank=True, verbose_name='资源分类ID')

    class Meta:
        db_table = 'ums_resource'
        verbose_name = '后台资源'
        verbose_name_plural = verbose_name


class UmsResourceCategory(models.Model):
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    name = models.CharField(max_length=200, null=True, blank=True, verbose_name='分类名称')
    sort = models.IntegerField(null=True, blank=True, verbose_name='排序')

    class Meta:
        db_table = 'ums_resource_category'
        verbose_name = '资源分类'
        verbose_name_plural = verbose_name


class UmsRole(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='名称')
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name='描述')
    admin_count = models.IntegerField(null=True, blank=True, verbose_name='后台用户数量')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    status = models.IntegerField(default=1, null=True, blank=True, verbose_name='启用状态：0->禁用；1->启用')
    sort = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        db_table = 'ums_role'
        verbose_name = '后台用户角色'
        verbose_name_plural = verbose_name


class UmsRoleMenuRelation(models.Model):
    role_id = models.BigIntegerField(null=True, blank=True, verbose_name='角色ID')
    menu_id = models.BigIntegerField(null=True, blank=True, verbose_name='菜单ID')

    class Meta:
        db_table = 'ums_role_menu_relation'
        verbose_name = '后台角色菜单关系'
        verbose_name_plural = verbose_name

class UmsRolePermissionRelation(models.Model):
    role_id = models.BigIntegerField(null=True, blank=True, verbose_name='角色ID')
    permission_id = models.BigIntegerField(null=True, blank=True, verbose_name='权限ID')

    class Meta:
        db_table = 'ums_role_permission_relation'
        verbose_name = '后台用户角色和权限关系'
        verbose_name_plural = verbose_name


class UmsRoleResourceRelation(models.Model):
    role_id = models.BigIntegerField(null=True, blank=True, verbose_name='角色ID')
    resource_id = models.BigIntegerField(null=True, blank=True, verbose_name='资源ID')

    class Meta:
        db_table = 'ums_role_resource_relation'
        verbose_name = '后台角色资源关系'
        verbose_name_plural = verbose_name
