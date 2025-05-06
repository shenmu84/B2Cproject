from django.db import models

# Create your models here.
class UmsMenu(models.Model):
    parent_id = models.BigIntegerField(null=True, blank=True, verbose_name='父级ID')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name='菜单名称')
    level = models.IntegerField(null=True, blank=True, verbose_name='菜单级数')
    sort = models.IntegerField(null=True, blank=True, verbose_name='菜单排序')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='前端名称')
    icon = models.CharField(max_length=200, null=True, blank=True, verbose_name='前端图标')
    hidden = models.IntegerField(null=True, blank=True, verbose_name='前端隐藏')

    class Meta:
        db_table = 'ums_menu'
        verbose_name = '后台菜单'
        verbose_name_plural = verbose_name

# DTO (Data Transfer Object) 类，用于封装菜单和子菜单
class UmsMenuNode(UmsMenu):
    children = models.JSONField(null=True, blank=True, verbose_name='子级菜单')

    class Meta:
        db_table = 'ums_menu_node'
        verbose_name = '后台菜单节点'
        verbose_name_plural = verbose_name

    # 如果需要在查询时返回子菜单，可以通过递归查询数据库来填充 `children` 字段
    def get_children(self):
        return UmsMenuNode.objects.filter(parent_id=self.id)
